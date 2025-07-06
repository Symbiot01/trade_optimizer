from app.db.queries import load_candidate_warehouses

# Example coordinates: B = Delhi, C = Mumbai
B = {"lat": 28.7041, "lon": 77.1025}  # Delhi
A = {"lat": 18.5204, "lon":73.8567}  # Pune
C = {"lat": 19.0760, "lon": 72.8777}  # Mumbai

def test_load_candidate_warehouses():
    print("Testing load_candidate_warehouses...")

    candidates = load_candidate_warehouses(A, C, max_detour_km=70)
    
    assert isinstance(candidates, list), "Expected list of candidates"
    for w in candidates:
        assert "warehouse_id" in w
        assert "lat" in w and "lon" in w
        print(f"Warehouse {w['warehouse_id']} @ ({w['lat']}, {w['lon']})")

    print(f"Total candidates found: {len(candidates)}")

if __name__ == "__main__":
    test_load_candidate_warehouses()
