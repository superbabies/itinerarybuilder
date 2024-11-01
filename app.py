from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv
from database import create_connection
from itinerary_builder import build_itinerary

load_dotenv()

app = FastAPI()

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ItineraryRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    activities: list

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Before Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logging.info(f"After Request: {request.method} {request.url.path} - Status: {response.status_code}")
    return response

@app.get("/")
async def home():
    return {"response": "Hello from Itinerary Builder!"}

"""
Generate an itinerary based on the provided parameters.
@params: destination, start_date, end_date, activities
destination: str
start_date: str
end_date: str
activities: list[int] (list of activity IDs)
"""
@app.post("/generate_itinerary")
async def generate_itinerary(request: ItineraryRequest):
    data = request.dict()
    

    destination = data['destination']
    start_date = data['start_date']
    end_date = data['end_date']
    activities = data['activities']
    
    if not destination or not start_date or not end_date or not activities:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    
    itinerary = build_itinerary(start_date, end_date, activities)


    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO itinerary_builder.itineraries (destination, start_date, end_date) VALUES (%s, %s, %s)", (destination, start_date, end_date))
    connection.commit()
    itinerary_id = cursor.lastrowid
    for day in itinerary:
        cursor.execute("INSERT INTO itinerary_builder.days (itinerary_id) VALUES (%s)", (itinerary_id,))
        connection.commit()
        day_id = cursor.lastrowid
        for event in day['activities']:
            cursor.execute("INSERT INTO itinerary_builder.day_events (day_id, event_id, start_time, end_time) VALUES (%s, %s, %s, %s)", (day_id, event['activity'], event['start_time'], event['end_time']))
            connection.commit()
        connection.commit()
    connection.close()


    response = {
        "itinerary_id": itinerary_id,
        "itinerary": itinerary,
        "links": {
            "self": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?id={itinerary_id}",
            "all_itineraries": "{}/get_itineraries".format(os.getenv('ITINERARY_BUILDER_URL'))
        }
    }

    return response
"""
Get itineraries based on the provided ID.
query @params: itinerary id (int)
"""
@app.get("/get_itineraries")
async def get_itineraries(request: Request):
    id = request.query_params.get('id')

    # return all itineraries if no ID is provided (default)
    if not id:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM itinerary_builder.itineraries")
        itineraries = cursor.fetchall()
        connection.close()

        response = {
            "itineraries": itineraries,
            "links": {
                "self": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries",
                "create_itinerary": f"{os.getenv('ITINERARY_BUILDER_URL')}/generate_itinerary"
            }
        }

        return response, 200

    logging.info(f"Requested ID: {id}")

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM itinerary_builder.itineraries WHERE itinerary_id = %s", (id,))
    itinerary = cursor.fetchone()
    cursor.execute("SELECT * FROM itinerary_builder.days WHERE itinerary_id = %s", (id,))
    itinerary_days = cursor.fetchall()
    connection.close()

    if not itinerary:
        raise HTTPException(status_code=404, detail=f"Itinerary not found for ID {id}")


    response = {
        "itinerary": itinerary,
        "itinerary_days": itinerary_days,
        "links": {
            "self": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?id={id}",
            "all_itineraries": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries",
            "create_itinerary": f"{os.getenv('ITINERARY_BUILDER_URL')}/generate_itinerary"
        }
    }

    return response, 200

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level="info")