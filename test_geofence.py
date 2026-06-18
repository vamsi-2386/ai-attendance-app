import sys
import os

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.geofence import validate_location

def test_circular_geofence():
    print("--- Testing Circular Geofence ---")
    offices = [
        {
            "id": "office_1",
            "type": "circular",
            "lat": 12.9716,
            "lon": 77.5946,
            "radius_meters": 100
        }
    ]
    
    # Point inside (same coordinates)
    res = validate_location(12.9716, 77.5946, offices)
    print(f"Inside check: {'Passed' if res else 'Failed'}")
    
    # Point outside (about 1km away)
    res = validate_location(12.9806, 77.5946, offices)
    print(f"Outside check: {'Passed' if not res else 'Failed'}")

def test_polygon_geofence():
    print("--- Testing Polygon Geofence ---")
    offices = [
        {
            "id": "office_2",
            "type": "polygon",
            "polygon_data": [
                (12.9710, 77.5940),
                (12.9720, 77.5940),
                (12.9720, 77.5950),
                (12.9710, 77.5950)
            ]
        }
    ]
    
    # Point inside the square
    res = validate_location(12.9715, 77.5945, offices)
    print(f"Inside check: {'Passed' if res else 'Failed'}")
    
    # Point outside the square
    res = validate_location(12.9730, 77.5960, offices)
    print(f"Outside check: {'Passed' if not res else 'Failed'}")

def test_multi_zone():
    print("--- Testing Multi-Zone Geofence ---")
    offices = [
        {
            "id": "office_1",
            "type": "circular",
            "lat": 12.9716,
            "lon": 77.5946,
            "radius_meters": 100
        },
        {
            "id": "office_2",
            "type": "polygon",
            "polygon_data": [
                (10.0, 10.0),
                (10.0, 11.0),
                (11.0, 11.0),
                (11.0, 10.0)
            ]
        }
    ]
    
    # Point inside office 2
    res = validate_location(10.5, 10.5, offices)
    print(f"Multi-zone check 1 (inside office 2): {'Passed' if res and res['id'] == 'office_2' else 'Failed'}")
    
    # Point inside office 1
    res = validate_location(12.9716, 77.5946, offices)
    print(f"Multi-zone check 2 (inside office 1): {'Passed' if res and res['id'] == 'office_1' else 'Failed'}")
    
    # Point outside both
    res = validate_location(0.0, 0.0, offices)
    print(f"Multi-zone check 3 (outside both): {'Passed' if not res else 'Failed'}")

if __name__ == "__main__":
    test_circular_geofence()
    test_polygon_geofence()
    test_multi_zone()
