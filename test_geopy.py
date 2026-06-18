import sys
from geopy.distance import geodesic

def test_distance():
    lat1, lon1 = 15.774400, 77.483200
    lat2, lon2 = "15.774400", "77.483200"
    radius = "100"
    
    try:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        dist = geodesic(point1, point2).meters
        print("Distance:", dist)
    except Exception as e:
        print("Geodesic Error:", type(e), e)
        
    try:
        print("Comparison:", dist <= float(radius))
    except Exception as e:
        print("Comparison Error:", type(e), e)
        
test_distance()
