import os
import math
import openrouteservice
from openrouteservice import Client

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometers between two points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    lat1, lat2 = math.radians(lat1), math.radians(lat2)

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Initialize client globally to reuse connections
client = openrouteservice.Client(key=os.getenv("ORS_API_KEY"))

def get_travel_time_minutes(lat1, lon1, lat2, lon2):
    """
    Query OpenRouteService for driving-car route duration in minutes.
    """
    coords = ((lon1, lat1), (lon2, lat2))
    res = client.directions(coords, profile="driving-car", format="geojson")
    duration_sec = res["features"][0]["properties"]["summary"]["duration"]
    return duration_sec / 60.0

def generate_warehouse_distance_matrix(warehouses, start_location, end_location):
    """
    warehouses: List of dicts with keys: warehouse_id, lat, lon
    start_location: tuple(lat, lon)
    end_location: tuple(lat, lon)

    Returns:
        unique_ids: list of warehouse IDs
        distances: full matrix
        durations: full matrix
        helper dicts for constant-time lookup
    """
    # Remove duplicates
    seen = set()
    unique_warehouses = []
    unique_ids = []

    for w in warehouses:
        if w["warehouse_id"] not in seen:
            seen.add(w["warehouse_id"])
            unique_warehouses.append(w)
            unique_ids.append(w["warehouse_id"])

    # Build coordinates: [source, *warehouses, destination]
    coords = [start_location] + [(w["lon"], w["lat"]) for w in unique_warehouses] + [end_location]

    ors_client = Client(key=os.getenv("ORS_API_KEY"))

    matrix = ors_client.distance_matrix(
        locations=coords,
        profile="driving-car",
        metrics=["distance", "duration"],
        units="m",
        optimized=False
    )

    distances = matrix["distances"]
    durations = matrix["durations"]

    # Map warehouse_id -> index in matrix (offset by +1 because of start_location)
    id_to_index = {wid: idx + 1 for idx, wid in enumerate(unique_ids)}

    # Build lookup dicts
    dist_lookup = {}
    time_lookup = {}
    for i, ida in enumerate(unique_ids):
        dist_lookup[ida] = {}
        time_lookup[ida] = {}
        for j, idb in enumerate(unique_ids):
            dist_lookup[ida][idb] = distances[i+1][j+1]
            time_lookup[ida][idb] = durations[i+1][j+1]

    # Distances/durations from source to each warehouse
    dist_from_source = {}
    time_from_source = {}
    for i, wid in enumerate(unique_ids):
        dist_from_source[wid] = distances[0][i+1]
        time_from_source[wid] = durations[0][i+1]

    # Distances/durations to destination
    dist_to_dest = {}
    time_to_dest = {}
    for i, wid in enumerate(unique_ids):
        dist_to_dest[wid] = distances[i+1][-1]
        time_to_dest[wid] = durations[i+1][-1]

    # Distances/durations from source to destination
    dist_source_dest = distances[0][-1]
    time_source_dest = durations[0][-1]

    return {
        "warehouse_ids": unique_ids,
        "distances": distances,
        "durations": durations,
        "dist_lookup": dist_lookup,
        "time_lookup": time_lookup,
        "dist_from_source": dist_from_source,
        "time_from_source": time_from_source,
        "dist_to_dest": dist_to_dest,
        "time_to_dest": time_to_dest,
        "dist_source_to_dest": dist_source_dest,
        "time_source_to_dest": time_source_dest,
        "get_helpers": lambda: (
            lambda wa, wb: (
                time_lookup[wa][wb], dist_lookup[wa][wb]
            ),
            lambda wa: (
                time_from_source[wa], dist_from_source[wa]
            ),
            lambda wa: (
                time_to_dest[wa], dist_to_dest[wa]
            )
        )
    }