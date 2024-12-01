from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv
from database import create_connection
from itinerary_builder import build_itinerary
from datetime import datetime, timedelta, timezone

load_dotenv(override=True)

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
    user_id: str

class RemoveEventRequest(BaseModel):
    event_id: int
    itinerary_id: int

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
    user_id = data['user_id']
    
    if not destination or not start_date or not end_date or not activities or not user_id:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    
    itinerary = build_itinerary(start_date, end_date, activities)

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO itinerary_builder.itineraries (user_id, destination, start_date, end_date) VALUES (%s, %s, %s, %s)", (user_id, destination, start_date, end_date))
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
            "self": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?user_id={user_id}&id={itinerary_id}",
            "all_itineraries": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?user_id={user_id}"
        }
    }

    return response, 201
"""
Get itineraries based on the provided ID.
query @params: itinerary id (int)
"""
@app.get("/get_itineraries")
async def get_itineraries(request: Request):
    id = request.query_params.get('id')
    user_id = request.query_params.get('user_id')

    # return all itineraries if no ID is provided (default)
    if not id:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM itinerary_builder.itineraries WHERE user_id = %s", (user_id,))
        itineraries = cursor.fetchall()
        connection.close()

        response = {
            "itineraries": itineraries,
            "links": {
                "self": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?user_id={user_id}",
                "generate_itinerary": f"{os.getenv('ITINERARY_BUILDER_URL')}/generate_itinerary"
            }
        }

        return response, 200

    logging.info(f"Requested ID: {id}")

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM itinerary_builder.itineraries WHERE itinerary_id = %s AND user_id = %s", (id, user_id,))
    itinerary = cursor.fetchone()
    cursor.execute("SELECT * FROM itinerary_builder.days WHERE itinerary_id = %s", (id,))
    itinerary_days = cursor.fetchall()
    start_date = itinerary['start_date']
    end_date = itinerary['end_date']
    list_of_days = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end_date - start_date).days + 1)]
    day_idx = 0
    for day in itinerary_days:
        cursor.execute("SELECT * FROM itinerary_builder.day_events WHERE day_id = %s", (day["day_id"],))
        day_events = cursor.fetchall()
        day["events"] = day_events
        day_date = datetime.strptime(list_of_days[day_idx], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        day["utc_date"] = day_date.isoformat()
        day_idx += 1
    connection.close()

    if not itinerary:
        raise HTTPException(status_code=404, detail=f"Itinerary not found for ID {id} and user ID {user_id}")


    response = {
        "itinerary": itinerary,
        "itinerary_days": itinerary_days,

        "destination": itinerary['destination'],
        "links": {
            "self": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?user_id={user_id}&id={id}",
            "all_itineraries": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?user_id={user_id}",
            "create_itinerary": f"{os.getenv('ITINERARY_BUILDER_URL')}/generate_itinerary"
        }
    }

    return response, 200

"""
Remove a specified event from an itinerary.
@params: day_events_id, itinerary_id
day_events_id: int
itinerary_id: int
"""
@app.patch("/remove_event")
async def remove_event(request: RemoveEventRequest):
    data = request.dict()
    
    event_id = data['event_id']
    itinerary_id = data['itinerary_id']
    
    connection = create_connection()
    cursor = connection.cursor()
    

    cursor.execute("SELECT * FROM itinerary_builder.day_events WHERE event_id = %s AND itinerary_id = %s", (event_id, itinerary_id,))
    event = cursor.fetchone()
    
    if not event:
        connection.close()
        raise HTTPException(status_code=404, detail="Event not found within the specified itinerary")
    

    cursor.execute("DELETE FROM itinerary_builder.day_events WHERE event_id = %s", (event_id,))
    connection.commit()
    connection.close()
    
    response = {
        "message": "Event removed successfully",
        "links": {
            "self": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries?id={itinerary_id}",
            "all_itineraries": f"{os.getenv('ITINERARY_BUILDER_URL')}/get_itineraries"
        }
    }
    
    return response, 200

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level="info")