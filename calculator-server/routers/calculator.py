# calculator.py
import math
from fastapi import APIRouter, Depends
from asteval import Interpreter

from schemas import Expression
from dependencies import get_history, need_increment

router = APIRouter(tags=["calculator"])

# ---------- Safe evaluator ----------
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})

@router.post("/calculate")
def calculate(expr: Expression, history_mgr=Depends(get_history), increment=Depends(need_increment)):
    try:
        code = expr.expand_percent()
        code = code.replace('Ã·', '/').replace('Ã—', '*')
        result = aeval(code)
        
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": expr, "result": "", "error": msg}
        
        # Add to history using dependency
        history_mgr.add_calculation(expr.expr, result)
        
        return {"ok": True, "expr": expr, "result": result, "error": ""}
    except Exception as e:
        return {"ok": False, "expr": expr, "error": str(e)}