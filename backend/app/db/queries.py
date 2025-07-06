from typing import List, Dict
from sqlalchemy import text
from app.db.db_session import get_db


def load_candidate_warehouses(B: Dict, C: Dict, max_detour_km: float = 30) -> List[Dict]:
    """
    Loads warehouses near the B–C segment where total detour B→W→C is within max_detour_km.
    Returns list of dicts with warehouse_id, lat, lon, and WKT location.
    """
    db = next(get_db())  

    sql = text("""
        SELECT
            w.id AS warehouse_id,
            ST_Y(w.location::geometry) AS lat,
            ST_X(w.location::geometry) AS lon
        FROM warehouses w
        WHERE
            ST_Distance(
                w.location,
                ST_SetSRID(ST_MakePoint(:blon, :blat), 4326)::geography
            ) +
            ST_Distance(
                w.location,
                ST_SetSRID(ST_MakePoint(:clon, :clat), 4326)::geography
            ) -
            ST_Distance( 
                ST_SetSRID(ST_MakePoint(:blon, :blat), 4326)::geography,
                ST_SetSRID(ST_MakePoint(:clon, :clat), 4326)::geography
            )
            <= :max_detour_meters
    """)


    result = db.execute(sql, {
        "blat": B["lat"], "blon": B["lon"],
        "clat": C["lat"], "clon": C["lon"],
        "max_detour_meters": max_detour_km * 1000
    })

    return [
        {
            "warehouse_id": row.warehouse_id,
            "lat": row.lat,
            "lon": row.lon
        }
        for row in result.fetchall()
    ]

def load_warehouses_by_item(
    src_lat: float,
    src_lon: float,
    dest_lat: float,
    dest_lon: float,
    max_detour_meters: float,
    max_load_capacity: float,
    cost_per_km: float
) -> List[Dict]:
    
    db = next(get_db())

    sql = text("""
        WITH filtered_warehouses AS (
            SELECT
                w.id,
                w.location
            FROM warehouses w
            WHERE
                ST_Distance(
                    w.location,
                    ST_SetSRID(ST_MakePoint(:src_lon, :src_lat), 4326)::geography
                ) +
                ST_Distance(
                    w.location,
                    ST_SetSRID(ST_MakePoint(:dest_lon, :dest_lat), 4326)::geography
                ) -
                ST_Distance(
                    ST_SetSRID(ST_MakePoint(:src_lon, :src_lat), 4326)::geography,
                    ST_SetSRID(ST_MakePoint(:dest_lon, :dest_lat), 4326)::geography
                )
                <= :max_detour_meters
        )
        SELECT
            wi.warehouse_id,
            wi.quantity,
            ST_Y(f.location::geometry) AS lat,
            ST_X(f.location::geometry) AS lon,
            i.id AS item_id,
            i.unit_weight,
            i.unit_volume,
            i.sell_price,
            i.buy_price,
            LEAST(
                wi.quantity * (i.sell_price - i.buy_price),
                :max_load_capacity * (i.sell_price - i.buy_price)/i.unit_weight
            ) -
            (
                (
                    (
                        ST_DistanceSphere(src_geom, f.location::geometry) * 1.25 +
                        ST_DistanceSphere(dest_geom, f.location::geometry) * 0.75
                    ) / 2
                ) * :cost_per_km
            ) AS demand_metric
        FROM warehouse_items wi
        JOIN items i
          ON wi.item_id = i.id
        JOIN filtered_warehouses f
          ON wi.warehouse_id = f.id,
          (SELECT ST_SetSRID(ST_MakePoint(:src_lon, :src_lat), 4326) AS src_geom) src,
          (SELECT ST_SetSRID(ST_MakePoint(:dest_lon, :dest_lat), 4326) AS dest_geom) dest
        ORDER BY demand_metric DESC
        LIMIT 50;
    """)

    result = db.execute(sql, {
        "max_detour_meters": max_detour_meters,
        "src_lon": src_lon,
        "src_lat": src_lat,
        "dest_lon": dest_lon,
        "dest_lat": dest_lat,
        "max_load_capacity": max_load_capacity,
        "cost_per_km": cost_per_km
    })

    rows = result.fetchall()

    warehouses = []
    for row in rows:
        warehouses.append({
            "warehouse_id": row.warehouse_id,
            "quantity": row.quantity,
            "lat": row.lat,
            "lon": row.lon,
            "item_id": row.item_id,
            "unit_weight": row.unit_weight,
            "unit_volume": row.unit_volume,
            "sell_price": row.sell_price,
            "buy_price": row.buy_price,
            "demand_metric": row.demand_metric
        })

    return warehouses