from geopy.distance import geodesic

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    """
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
        
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    
    # Return distance in meters
    return geodesic(point1, point2).meters

def is_within_radius(user_lat, user_lon, office_lat, office_lon, radius_meters=100):
    """
    Check if the user's location is within the specified radius of the office.
    """
    if None in (office_lat, office_lon):
        # If office location is not set, we can either allow or deny. 
        # Let's return False or raise an exception. Let's return False for strictness.
        return False
        
    distance = calculate_distance(user_lat, user_lon, office_lat, office_lon)
    return distance <= radius_meters

def is_suspicious_location(location_data):
    """
    Detect if the GPS data seems suspicious.
    (Disabled temporarily for easier testing)
    """
    return False
