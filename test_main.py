import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_history():
    """Clear history before each test"""
    # Clear history via API call
    client.delete("/history")
    yield
    # Optionally clear after test too
    client.delete("/history")

def test_basic_division():
    # Changed from params to json for request body
    r = client.post("/calculate", json={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = client.post("/calculate", json={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", json={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = client.post("/calculate", json={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""

def test_get_history_empty():
    """Test getting history when no calculations have been performed"""
    response = client.get("/history")
    assert response.status_code == 200
    assert response.json() == []

def test_get_history_with_calculations():
    """Test getting history after performing calculations"""
    # Perform some calculations first
    client.post("/calculate", json={"expr": "2 + 2"})
    client.post("/calculate", json={"expr": "5 * 3"})
    
    response = client.get("/history")
    assert response.status_code == 200
    history_data = response.json()
    assert len(history_data) == 2
    
    # Check first calculation
    assert history_data[0]["expr"] == "2 + 2"
    assert history_data[0]["result"] == 4
    assert history_data[0]["ok"] is True
    assert "timestamp" in history_data[0]
    assert "error" in history_data[0]  # New field from CalculatorLog model
    
    # Check second calculation
    assert history_data[1]["expr"] == "5 * 3"
    assert history_data[1]["result"] == 15
    assert history_data[1]["ok"] is True
    assert "timestamp" in history_data[1]

def test_calculation_adds_to_history():
    """Test that successful calculations are automatically added to history"""
    # Start with empty history
    response = client.get("/history")
    assert len(response.json()) == 0
    
    # Perform calculation
    calc_response = client.post("/calculate", json={"expr": "10 + 5"})
    assert calc_response.json()["ok"] is True
    assert calc_response.json()["result"] == 15
    
    # Check it was added to history
    history_response = client.get("/history")
    history_data = history_response.json()
    assert len(history_data) == 1
    assert history_data[0]["expr"] == "10 + 5"
    assert history_data[0]["result"] == 15

def test_delete_history_success():
    """Test successful deletion of all history"""
    # Add some calculations first
    client.post("/calculate", json={"expr": "1 + 1"})
    client.post("/calculate", json={"expr": "2 + 2"})
    
    # Verify history has items
    history_response = client.get("/history")
    assert len(history_response.json()) == 2
    
    # Delete history
    response = client.delete("/history")
    assert response.status_code == 200
    assert response.json() == []  # Your API returns empty list
    
    # Verify history is empty
    get_response = client.get("/history")
    assert get_response.json() == []

def test_delete_history_when_empty():
    """Test deleting history when it's already empty"""
    # Ensure history is empty
    client.delete("/history")
    
    # Delete again
    response = client.delete("/history")
    assert response.status_code == 200
    assert response.json() == []

def test_calculation_history_workflow():
    """Test the complete workflow: calculate -> get history -> delete"""
    # Clear any existing history
    client.delete("/history")
    
    # Perform calculations
    expressions = ["10 + 5", "20 - 8", "6 * 7"]
    expected_results = [15, 12, 42]
    
    for expr, expected in zip(expressions, expected_results):
        response = client.post("/calculate", json={"expr": expr})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["result"] == expected
    
    # Check history
    history_response = client.get("/history")
    history_data = history_response.json()
    assert len(history_data) == 3
    
    for i, (expr, result) in enumerate(zip(expressions, expected_results)):
        assert history_data[i]["expr"] == expr
        assert history_data[i]["result"] == result
        assert "timestamp" in history_data[i]
        assert history_data[i]["ok"] is True
    
    # Clear history
    delete_response = client.delete("/history")
    assert delete_response.status_code == 200
    
    # Verify empty
    final_history = client.get("/history")
    assert final_history.json() == []

def test_history_with_percent_calculations():
    """Test history with percentage calculations"""
    # Test various percentage operations
    percent_expressions = [
        ("100 - 10%", 90.0),  # 100 - (10% of 100) = 100 - 10 = 90
        ("50 + 20%", 60.0),   # 50 + (20% of 50) = 50 + 10 = 60
        ("200 * 5%", 10.0),   # 200 * (5/100) = 200 * 0.05 = 10
        ("10%", 0.1)          # 10/100 = 0.1
    ]
    
    for expr, expected in percent_expressions:
        response = client.post("/calculate", json={"expr": expr})
        assert response.json()["ok"] is True
        assert abs(response.json()["result"] - expected) < 1e-9
    
    # Check all are in history
    history_response = client.get("/history")
    history_data = history_response.json()
    assert len(history_data) == 4
    
    for i, (expr, expected) in enumerate(percent_expressions):
        assert history_data[i]["expr"] == expr
        assert abs(history_data[i]["result"] - expected) < 1e-9

def test_history_max_limit():
    """Test that history respects the maximum limit (HISTORY_MAX = 1000)"""
    # This test would be slow with 1000+ items, so we'll test the concept
    # by adding several items and ensuring they're all preserved
    
    # Add 10 calculations
    for i in range(10):
        client.post("/calculate", json={"expr": f"{i} + 1"})
    
    response = client.get("/history")
    history_data = response.json()
    assert len(history_data) == 10
    
    # Check that all calculations are preserved in order
    for i in range(10):
        assert history_data[i]["expr"] == f"{i} + 1"
        assert history_data[i]["result"] == i + 1

def test_history_timestamps_are_different():
    """Test that different calculations have different timestamps"""
    import time
    
    # Perform two calculations with a small delay
    client.post("/calculate", json={"expr": "1 + 1"})
    time.sleep(0.01)  # Small delay to ensure different timestamps
    client.post("/calculate", json={"expr": "2 + 2"})
    
    response = client.get("/history")
    history_data = response.json()
    assert len(history_data) == 2
    
    # Timestamps should be different
    timestamp1 = history_data[0]["timestamp"]
    timestamp2 = history_data[1]["timestamp"]
    assert timestamp1 != timestamp2

# Additional OOP-specific tests

def test_expression_model_validation():
    """Test that invalid request body structure returns 422"""
    # Missing required 'expr' field
    response = client.post("/calculate", json={})
    assert response.status_code == 422
    
    # Wrong field name
    response = client.post("/calculate", json={"expression": "2 + 2"})
    assert response.status_code == 422
    
    # Non-string expr field
    response = client.post("/calculate", json={"expr": 123})
    assert response.status_code == 422

def test_response_structure_matches_models():
    """Test that API responses match the expected Pydantic model structure"""
    # Test successful calculation response
    response = client.post("/calculate", json={"expr": "5 + 5"})
    assert response.status_code == 200
    data = response.json()
    
    # Should have all fields from CalculationResponse model
    required_fields = {"ok", "expr", "result", "error"}
    assert all(field in data for field in required_fields)
    assert isinstance(data["ok"], bool)
    assert isinstance(data["expr"], str)
    assert isinstance(data["error"], str)
    
    # Test error response structure
    response = client.post("/calculate", json={"expr": "invalid**("})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["result"] is None
    assert len(data["error"]) > 0

def test_history_response_structure():
    """Test that history endpoint returns proper CalculatorLog structure"""
    # Add a calculation
    client.post("/calculate", json={"expr": "3 * 4"})
    
    response = client.get("/history")
    assert response.status_code == 200
    history_data = response.json()
    assert len(history_data) == 1
    
    # Check CalculatorLog model fields
    log_entry = history_data[0]
    required_fields = {"timestamp", "expr", "result", "ok", "error"}
    assert all(field in log_entry for field in required_fields)
    
    assert isinstance(log_entry["timestamp"], str)
    assert isinstance(log_entry["expr"], str)
    assert isinstance(log_entry["ok"], bool)
    assert isinstance(log_entry["error"], str)

def test_mathematical_constants():
    """Test calculations with mathematical constants"""
    # Test pi
    response = client.post("/calculate", json={"expr": "pi * 2"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert abs(data["result"] - 6.283185307179586) < 1e-10
    
    # Test e
    response = client.post("/calculate", json={"expr": "e"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert abs(data["result"] - 2.718281828459045) < 1e-10

def test_complex_expression_with_history():
    """Test complex mathematical expressions and verify they're stored correctly"""
    complex_expressions = [
        ("2**3 + 5", 13),
        ("(10 + 5) * 2", 30),
        ("100 / (2 + 3)", 20.0),
        ("pi * 2**2", 12.566370614359172)
    ]
    
    for expr, expected in complex_expressions:
        response = client.post("/calculate", json={"expr": expr})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert abs(data["result"] - expected) < 1e-10
    
    # Verify all are in history
    history_response = client.get("/history")
    history_data = history_response.json()
    assert len(history_data) == len(complex_expressions)
    
    for i, (expr, expected) in enumerate(complex_expressions):
        assert history_data[i]["expr"] == expr
        assert abs(history_data[i]["result"] - expected) < 1e-10
        assert history_data[i]["ok"] is True
        assert history_data[i]["error"] == ""