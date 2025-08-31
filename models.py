from pydantic import BaseModel
from typing import Union
from datetime import datetime

class Expression(BaseModel):
    """Request model for mathematical expression."""
    expr: str
    
    def expand_percent(self) -> str:
        """
        Expand percentage symbols in the expression.
        This method converts percentage notation to decimal form.
        For example: "50%" becomes "50/100" or "0.5"
        """
        from calculator import expand_percent
        return expand_percent(self.expr)
    
class CalculatorLog(BaseModel):
    """Response model for calculation log entry."""
    timestamp: str
    expr: str
    result: Union[float, str, int]
    ok: bool
    error: str = ""
    
class CalculationResponse(BaseModel):
    """Response model for calculation result."""
    ok: bool
    expr: str
    result: Union[float, str, int, None] = None
    error: str = ""
    