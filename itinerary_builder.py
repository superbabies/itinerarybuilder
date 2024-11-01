from datetime import datetime, timedelta
import pytz

def build_itinerary(start_date, end_date, activities):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    days = (end_date - start_date).days + 1
    itinerary = []
    

    day_start_time = datetime.strptime("09:00", "%H:%M").time()
    day_end_time = datetime.strptime("17:00", "%H:%M").time()
    activity_duration = timedelta(hours=2)
    

    utc_tz = pytz.utc
    

    activity_index = 0
    for i in range(days):
        day = start_date + timedelta(days=i)
        current_time = datetime.combine(day, day_start_time).replace(tzinfo=utc_tz)
        day_activities = []
        
        while current_time.time() < day_end_time:
            if activity_index >= len(activities):
                break
            
            activity = activities[activity_index]
            activity_index += 1
            
            day_activities.append({
                'start_time': current_time,
                'end_time': current_time + activity_duration,
                'activity': activity
            })
            current_time += activity_duration
        
        itinerary.append({
            'date': day.strftime("%Y-%m-%d"),
            'activities': day_activities
        })
    
    return itinerary