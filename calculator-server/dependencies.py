# dependencies.py
from collections import deque
from datetime import datetime
from schemas import CalculationLog

HISTORY_MAX = 1000

class HistoryManager:
    def __init__(self):
        self.history = deque(maxlen=HISTORY_MAX)
    
    def add_calculation(self, expr: str, result: any):
        """Add calculation to history"""
        self.history.appendleft(CalculationLog(
            timestamp=datetime.now().isoformat() + "Z",
            expr=expr,
            result=result
        ))
    
    def get_history(self, limit: int = 50) -> list[CalculationLog]:
        """Get calculation history with limit"""
        return list(self.history)[: max(0, min(limit, HISTORY_MAX))]
    
    def clear_history(self):
        """Clear all history"""
        self.history.clear()

# Global instance
history_manager = HistoryManager()

def get_history():
    """Dependency to get history manager"""
    return history_manager

def expand_parentheses(expr: str) -> str:
    """Expand parentheses in expression - moved from main.py"""
    # This function would handle parentheses expansion if needed
    # For now, we'll keep it simple since the original doesn't have this function
    return expr

def need_increment():
    """Dependency for increment functionality"""
    return True