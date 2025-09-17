import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_calculate_simple():
    """Test simple calculation"""
    response = client.post("/calculate", json={"expr": "2+2"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["result"] == 4
    assert data["error"] == ""

def test_calculate_multiplication():
    """Test multiplication"""
    response = client.post("/calculate", json={"expr": "3*4"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["result"] == 12

def test_calculate_division():
    """Test division"""
    response = client.post("/calculate", json={"expr": "10/2"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["result"] == 5.0

def test_calculate_percentage():
    """Test percentage calculation"""
    response = client.post("/calculate", json={"expr": "100 + 10%"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["result"] == 110.0

def test_calculate_error():
    """Test calculation error"""
    response = client.post("/calculate", json={"expr": "1/0"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == False
    assert "error" in data

def test_get_history():
    """Test get history endpoint"""
    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_clear_history():
    """Test clear history endpoint"""
    response = client.delete("/history")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["cleared"] == True

def test_get_history_with_limit():
    """Test get history with limit parameter"""
    response = client.get("/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10