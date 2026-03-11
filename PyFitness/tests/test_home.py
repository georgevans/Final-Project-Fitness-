from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
                    
def test_home_page_returns_200():
    response = client.get("/")
    assert response.status_code == 200