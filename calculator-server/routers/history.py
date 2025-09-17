from fastapi import APIRouter, Depends

from schemas import CalculationLog
from dependencies import get_history

router = APIRouter(tags=["history"])

@router.get("/history")
def get_calculation_history(limit: int = 50, history_mgr=Depends(get_history)) -> list[CalculationLog]:
    return history_mgr.get_history(limit)

@router.delete("/history")
def clear_history(history_mgr=Depends(get_history)):
    history_mgr.clear_history()
    return {"ok": True, "cleared": True}