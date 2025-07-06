from pydantic import BaseModel
from typing import List, Tuple, Dict

class OptimizationRequest(BaseModel):
    start_location: Tuple[float, float]
    end_location: Tuple[float, float]
    t_max: float
    cost_per_km_per_kg: float
    max_truck_weight_kg: float
    curr_truck_weight_kg: float

class ProfitPair(BaseModel):
    buy_warehouse_id: int
    sell_warehouse_id: int
    item_id: int
    traded_quantity: float
    gross_profit: float
    net_profit: float
    transport_cost: float
    unit_profit_per_kg: float
    T_AWb: float
    T_WbWs: float
    T_WsB: float
    D_AWb: float
    D_WbWs: float
    D_WsB: float
    extra_distance_km: float
    total_trip_time: float

class OptimizationResponse(BaseModel):
    profitable_pairs: List[ProfitPair]
