import math
from typing import List, Dict, Optional, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000 # Radius of earth in meters
    return c * r

def is_point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using the ray-casting algorithm.
    Polygon is a list of (lat, lon) tuples.
    """
    num_vertices = len(polygon)
    inside = False
    
    # Ray-casting
    p1x, p1y = polygon[0]
    for i in range(num_vertices + 1):
        p2x, p2y = polygon[i % num_vertices]
        if lat > min(p1x, p2x):
            if lat <= max(p1x, p2x):
                if lon <= max(p1y, p2y):
                    if p1x != p2x:
                        xints = (lat - p1x) * (p2y - p1y) / (p2x - p1x) + p1y
                    if p1x == p2x or lon <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
        
    return inside

def validate_location(user_lat: float, user_lon: float, offices: List[Dict]) -> Optional[Dict]:
    """
    Check if the user coordinates fall within any of the provided office geofences.
    
    offices: list of dicts. Example:
    [
        {
            "id": "office_1",
            "type": "circular",
            "lat": 12.9716,
            "lon": 77.5946,
            "radius_meters": 50
        },
        {
            "id": "office_2",
            "type": "polygon",
            "polygon_data": [(12.9, 77.5), (12.9, 77.6), (12.8, 77.6), (12.8, 77.5)]
        }
    ]
    
    Returns the matched office dict if valid, else None.
    """
    for office in offices:
        geofence_type = office.get('type', 'circular').lower()
        
        if geofence_type == 'circular':
            office_lat = office.get('lat')
            office_lon = office.get('lon')
            radius = office.get('radius_meters', 50)
            
            if office_lat is None or office_lon is None:
                continue
                
            dist = haversine_distance(user_lat, user_lon, float(office_lat), float(office_lon))
            if dist <= float(radius):
                return office
                
        elif geofence_type == 'polygon':
            polygon_data = office.get('polygon_data')
            if not polygon_data or not isinstance(polygon_data, list):
                continue
                
            if is_point_in_polygon(user_lat, user_lon, polygon_data):
                return office
                
    return None
