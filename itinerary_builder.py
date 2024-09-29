from datetime import datetime, timedelta

# Function to build the itinerary based on user input
def build_itinerary(destination, start_date, end_date, activities):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    days = (end_date - start_date).days + 1  # Calculate number of trip days
    itinerary = []
    
    # Build a day-by-day itinerary, rotating through the activities
    for i in range(days):
        day = start_date + timedelta(days=i)
        activity = activities[i % len(activities)]  # Rotate through activities if there are more days than activities
        itinerary.append({
            'date': day.strftime("%Y-%m-%d"),
            'destination': destination,
            'activity': activity
        })
    
    return itinerary