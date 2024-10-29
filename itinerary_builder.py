from datetime import datetime, timedelta

def build_itinerary(destination, start_date, end_date, activities):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    days = (end_date - start_date).days + 1 
    itinerary = []
    

    day_start_time = datetime.strptime("09:00", "%H:%M").time()
    day_end_time = datetime.strptime("17:00", "%H:%M").time()
    activity_duration = timedelta(hours=2)
    

    for i in range(days):
        day = start_date + timedelta(days=i)
        current_time = datetime.combine(day, day_start_time)
        day_activities = []
        
        while current_time.time() < day_end_time:
            activity = activities[(i * 4 + (current_time.hour - 9) // 2) % len(activities)] 
            day_activities.append({
                'start_time': current_time.strftime("%H:%M"),
                'end_time': (current_time + activity_duration).strftime("%H:%M"),
                'activity': activity
            })
            current_time += activity_duration
        
        itinerary.append({
            'date': day.strftime("%Y-%m-%d"),
            'destination': destination,
            'activities': day_activities
        })
    
    return itinerary


if __name__ == "__main__":
    destination = "Paris"
    start_date = "2023-10-01"
    end_date = "2023-10-05"
    activities = ["Visit Eiffel Tower", "Louvre Museum", "Seine River Cruise", "Notre Dame Cathedral", "Montmartre"]
    
    itinerary = build_itinerary(destination, start_date, end_date, activities)
    for day in itinerary:
        print(day)