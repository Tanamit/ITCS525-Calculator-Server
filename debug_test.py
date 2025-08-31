from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def debug_calculation():
    """Debug what's going wrong with calculations"""
    
    # Test simple calculation and print full response
    print("Testing simple calculation: 30/4")
    response = client.post("/calculate", json={"expr": "30/4"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test percentage calculation
    print("\nTesting percentage: 6%")
    response = client.post("/calculate", json={"expr": "6%"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test mathematical constant
    print("\nTesting pi constant: pi")
    response = client.post("/calculate", json={"expr": "pi"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    debug_calculation()