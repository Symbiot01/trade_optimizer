#routes.py

from fastapi import APIRouter
from app.models.schemas import OptimizationRequest, OptimizationResponse
from app.core.optimizer import find_profitable_pairs

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResponse)
def optimize_route(req: OptimizationRequest):
    pairs = find_profitable_pairs(
        start_location=req.start_location,
        end_location=req.end_location,
        t_max=req.t_max,
        cost_per_km_per_kg=req.cost_per_km_per_kg,
        max_truck_weight_kg=req.max_truck_weight_kg,
        curr_truck_weight_kg=req.curr_truck_weight_kg
    )
    return {"profitable_pairs": pairs}
