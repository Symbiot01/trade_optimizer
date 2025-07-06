# optimizer.py

from typing import Dict, List, Optional, Tuple
import math
from .geo_utils import generate_warehouse_distance_matrix, haversine_km
from app.db.queries import load_warehouses_by_item


def find_profitable_pairs(
    start_location: Tuple[float, float],
    end_location: Tuple[float, float],
    t_max: float,
    cost_per_km_per_kg: float,
    max_truck_weight_kg: float,
    curr_truck_weight_kg: float,
) -> List[Dict]:
    """
    Returns up to 30 most profitable buy-sell warehouse pairs.
    
    Args:
        start_location: (lat, lon) of A.
        end_location: (lat, lon) of B.
        t_max: max trip time (hours).
        cost_per_km_per_kg: transport cost per km per kg.
        max_truck_weight_kg: truck capacity in kg.
        get_time_distance: function(origin, dest) -> (time_hours, distance_km)
        
    Returns:
        List of profitable pairs sorted by descending net profit.
    """


    warehouses = load_warehouses_by_item(
        src_lat=start_location[0],
        src_lon=start_location[1],
        dest_lat=end_location[0],
        dest_lon=end_location[1],
        max_detour_meters=50000,  # 50 km detour limit
        max_load_capacity=max_truck_weight_kg,
        cost_per_km=cost_per_km_per_kg * max_truck_weight_kg  # To be edited (SQL query needs to be updated to use this value)
    )
    if not warehouses:
        return []  # No warehouses found
    
    # matrix_result = generate_warehouse_distance_matrix(
    #     warehouses,
    #     start_location,
    #     end_location
    # )
    # get_dist_time, get_dist_time_source, get_dist_time_dest = matrix_result["get_helpers"]()


# ---------------------------------------to be changed---------------------------------------

    t_max_count = 0
    q_max_count = 0
    net_profit_count = 0
    # Baseline A→B trip
    # raw_T_AB = matrix_result["time_source_to_dest"]
    # raw_D_AB = matrix_result["dist_source_to_dest"]
    raw_D_AB = None
    raw_T_AB = None

    
    if raw_D_AB is None:
        # Estimate straight-line distance
        D_AB = haversine_km(start_location[0], start_location[1], end_location[0], end_location[1])
    else:
        D_AB = raw_D_AB / 1000.0

    if raw_T_AB is None:
        # Estimate time assuming 25 km/h
        T_AB = D_AB / 25.0
        print(f"Fallback: estimated T_AB = {T_AB:.2f} hours for {D_AB:.2f} km.")
    else:
        T_AB = raw_T_AB / 3600.0

# ---------------------------------------to be changed---------------------------------------

    
    profitable_pairs = []

    for wb in warehouses:
        if wb["quantity"] <= 0:
            continue  # not a supplier
        for ws in warehouses:
            if ws["quantity"] >= 0:
                continue  # not a demand point
            if wb["item_id"] != ws["item_id"]:
                continue  # different items

# ---------------------------------------to be changed---------------------------------------

            # Segment 1: A to Buy warehouse
            # T_AWb_sec, D_AWb_m = get_dist_time_source(wb["warehouse_id"])
            T_AWb_sec, D_AWb_m = None, None  # To be changed to use the new function
            if T_AWb_sec is None or D_AWb_m is None:
                D_AWb = haversine_km(
                    start_location[0], start_location[1],
                    wb["lat"], wb["lon"]
                )
                T_AWb = D_AWb / 25.0
                print(f"Fallback A->Wb: {D_AWb:.2f} km, {T_AWb:.2f} hrs.")
            else:
                D_AWb = D_AWb_m / 1000.0
                T_AWb = T_AWb_sec / 3600.0

            # Segment 2: Wb to Ws
            # T_WbWs_sec, D_WbWs_m = get_dist_time(wb["warehouse_id"], ws["warehouse_id"])
            T_WbWs_sec, D_WbWs_m = None, None  # To be changed to use the new function
            if T_WbWs_sec is None or D_WbWs_m is None:
                D_WbWs = haversine_km(
                    wb["lat"], wb["lon"],
                    ws["lat"], ws["lon"]
                )
                T_WbWs = D_WbWs / 25.0
                print(f"Fallback Wb->Ws: {D_WbWs:.2f} km, {T_WbWs:.2f} hrs.")
            else:
                D_WbWs = D_WbWs_m / 1000.0
                T_WbWs = T_WbWs_sec / 3600.0

            # Segment 3: Ws to B
            # T_WsB_sec, D_WsB_m = get_dist_time_dest(ws["warehouse_id"])
            T_WsB_sec, D_WsB_m = None, None  # To be changed to use the new function
            if T_WsB_sec is None or D_WsB_m is None:
                D_WsB = haversine_km(
                    ws["lat"], ws["lon"],
                    end_location[0], end_location[1]
                )
                T_WsB = D_WsB / 25.0
                print(f"Fallback Ws->B: {D_WsB:.2f} km, {T_WsB:.2f} hrs.")
            else:
                D_WsB = D_WsB_m / 1000.0
                T_WsB = T_WsB_sec / 3600.0

# ---------------------------------------to be changed---------------------------------------

            T_total = T_AWb + T_WbWs + T_WsB

            if T_total > t_max:
                t_max_count += 1
                print(f"Skipping pair {wb['warehouse_id']} -> {ws['warehouse_id']} due to time limit.")
                continue  # exceeds deadline

            # Max feasible quantity
            q_available = min(wb["quantity"], abs(ws["quantity"]))
            q_capacity_limit = max_truck_weight_kg / wb["unit_weight"]
            q_max = math.floor(min(q_available, q_capacity_limit))

            if q_max <= 0:
                q_max_count += 1
                print(f"Skipping pair {wb['warehouse_id']} -> {ws['warehouse_id']} due to insufficient quantity.")
                continue  # nothing can be carried

            # Profits and costs
            unit_gross_profit = abs(ws["sell_price"] - wb["buy_price"])
            gross_profit = unit_gross_profit * q_max
            extra_distance_km = (D_AWb + D_WbWs + D_WsB) - D_AB
            transport_cost = extra_distance_km * cost_per_km_per_kg * (q_max * wb["unit_weight"])
            net_profit = gross_profit - transport_cost
            unit_profit_per_kg = unit_gross_profit / wb["unit_weight"]

            if net_profit <= 0:
                print(f"Skipping pair {wb['warehouse_id']} -> {ws['warehouse_id']} due to non-profitable trade.")
                net_profit_count += 1
                continue  # not profitable

            profitable_pairs.append({
                "buy_warehouse_id": wb["warehouse_id"],
                "sell_warehouse_id": ws["warehouse_id"],
                "item_id": wb["item_id"],
                "traded_quantity": q_max,
                "gross_profit": gross_profit,
                "net_profit": net_profit,
                "transport_cost": transport_cost,
                "unit_profit_per_kg": unit_profit_per_kg,
                "T_AWb": T_AWb,
                "T_WbWs": T_WbWs,
                "T_WsB": T_WsB,
                "D_AWb": D_AWb,
                "D_WbWs": D_WbWs,
                "D_WsB": D_WsB,
                "extra_distance_km": extra_distance_km,
                "total_trip_time": T_total
            })

    # Sort descending by net profit
    profitable_pairs.sort(key=lambda x: x["net_profit"], reverse=True)

    print(f"Total pairs found: {len(profitable_pairs)}")
    print(f"Pairs exceeding time limit: {t_max_count}")
    print(f"Pairs with insufficient quantity: {q_max_count}")
    print(f"Pairs with non-profitable trades: {net_profit_count}")
    # Return top 30
    return profitable_pairs[:30]





