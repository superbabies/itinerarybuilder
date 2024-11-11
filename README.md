
# Itinerary Builder Microservice

This microservice allows users to generate, update, and retrieve travel itineraries. It provides endpoints to create new itineraries, update existing ones, and fetch itineraries based on provided parameters.

## Table of Contents

- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Endpoints](#endpoints)
  - [Generate Itinerary](#generate-itinerary)
  - [Update Itinerary](#update-itinerary)
  - [Get Itineraries](#get-itineraries)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/superbabies/itinerary-builder.git
   cd itinerary-builder
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   
## Environment Variables
Create a `.env` file in the project directory and add the following environment variables:
  ```sh
  DB_IP=your_database_ip
  DB_USER=your_database_user
  DB_PASSWORD=your_database_password
  OPENCAGE_API_KEY=your_opencage_api_key
  ITINERARY_BUILDER_URL=http://localhost:8000
  ```
  
## Running the App
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

## Endpoints
**Generate Itinerary**
- URL: /generate_itinerary
- Method: POST
- Description: Generates a new itinerary based on the provided parameters.
- Request Body:
```sh
{
  "destination": "Paris",
  "start_date": "2023-10-01",
  "end_date": "2023-10-05",
  "activities": [1, 2, 3]
}
- Response:
```sh
{
  "itinerary_id": 1,
  "itinerary": [
    {
      "date": "2023-10-01",
      "destination": "Paris",
      "activities": [
        {
          "start_time": "2023-10-01T09:00:00+00:00",
          "end_time": "2023-10-01T11:00:00+00:00",
          "activity": "Visit Eiffel Tower"
        }
      ]
    }
  ],
  "links": {
    "self": "http://localhost:5000/get_itineraries?id=1",
    "all_itineraries": "http://localhost:5000/get_itineraries"
  }
}
```

**Get Itineraries**
- URL: /get_itineraries
- Method: GET
- Description: Retrieves itineraries based on the provided ID. If no ID is provided, returns all itineraries.
- Query Parameters: `id` (optional): The ID of the itinerary to retrieve.
- Response:
```sh
{
  "itineraries": [
    {
      "itinerary_id": 1,
      "destination": "Paris",
      "start_date": "2023-10-01",
      "end_date": "2023-10-05"
    }
  ],
  "links": {
    "self": "http://localhost:5000/get_itineraries",
    "create_itinerary": "http://localhost:5000/generate_itinerary"
  }
}
