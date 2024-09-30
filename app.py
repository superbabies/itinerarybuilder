from flask import Flask, jsonify, request
from flask_cors import CORS

from itinerary_builder import build_itinerary

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'response': "Hello from Itinerary Builder!"})

# Endpoint to receive user preferences and build an itinerary
# Basic for now but will be expanded upon to call DB
# and other services to get more data
# Hardcode most data for now
# Other microservices will eventually be called to get this data
@app.route('/generate_itinerary', methods=['POST'])
def generate_itinerary():
    data = request.json  # Get the input data as JSON
    
    if not data or 'destination' not in data or 'start_date' not in data or 'end_date' not in data or 'activities' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Extract the input data
    destination = data['destination']
    start_date = data['start_date']
    end_date = data['end_date']
    activities = data['activities']  # This should be a list of activities
    
    # Call the itinerary builder function
    itinerary = build_itinerary(destination, start_date, end_date, activities)

    # Export itinerary to Google Calendar
    # This will be implemented in future 
    
    return jsonify(itinerary), 200



if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=8000, debug=True))