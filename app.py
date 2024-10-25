from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from itinerary_builder import build_itinerary

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
    return itinerary

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level="info")