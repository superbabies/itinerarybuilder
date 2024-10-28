import uuid
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from itinerary_builder import build_itinerary
from database import create_connection

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

# Define Pydantic models for request validation
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

@app.post("/generate_itinerary")
async def generate_itinerary(request: ItineraryRequest):
    data = request.dict()  # Convert Pydantic model to dictionary
    
    # Extract the input data
    destination = data['destination']
    start_date = data['start_date']
    end_date = data['end_date']
    activities = data['activities']  # This should be a list of activities
    
    if not destination or not start_date or not end_date or not activities:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    itinerary = build_itinerary(destination, start_date, end_date, activities)

    # Generate a unique ID for the itinerary
    itinerary_id = str(uuid.uuid4())

    # Post to database using mysql-connector
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO itinerary_builder.itineraries (id, destination, start_date, end_date, activities) VALUES (%s, %s, %s, %s, %s)", (itinerary_id, destination, start_date, end_date, str(activities)))
    connection.commit()
    connection.close()

    return itinerary_id, itinerary

@app.get("/get_itineraries")
async def get_itineraries(request: Request):
    id = request.query_params.get('id')

    logging.info(f"Requested ID: {id}")

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM itinerary_builder.itineraries WHERE itinerary_id = %s", (id,))
    itinerary = cursor.fetchall()
    logging.info(f"Returned Itinerary: {itinerary}")
    connection.close()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found for itinerary ID {}".format(id))

    return itinerary

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level="info")