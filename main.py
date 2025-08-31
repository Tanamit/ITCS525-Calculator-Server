import math
from collections import deque
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

from models import CalculationResponse, Expression, CalculatorLog
HISTORY_MAX = 1000
history = deque(maxlen=HISTORY_MAX)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Safe evaluator ----------
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})


@app.post("/calculate", response_model=CalculationResponse)
def calculate(expr: Expression)-> CalculationResponse:
    try:
        code = expr.expand_percent()
        result = aeval(code)
        
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return CalculationResponse(ok=False, expr=expr.expr, error=msg)
        # TODO: Add history
        history_entry = CalculatorLog(
            timestamp=datetime.utcnow().isoformat(),
            expr=expr.expr,
            result=result,
            ok=True,
            error=""
        )
        history.append(history_entry)
        return CalculationResponse(ok=True, expr=expr.expr, result=result)
    except Exception as e:
        return CalculationResponse(ok=False, expr=expr.expr, error=str(e))

# TODO GET /hisory

@app.get("/history", response_model=list[CalculatorLog])
def get_history() -> list[CalculatorLog]:
    """
    Get the calculation history.
    Returns a list of all calculations with timestamps.
    """
    return list(history)

# TODO DELETE /history

@app.delete("/history", response_model=list[CalculatorLog])
def clear_history() -> list[CalculatorLog]:
    """
    Clear all calculation history.
    """
    history.clear()
    return []


