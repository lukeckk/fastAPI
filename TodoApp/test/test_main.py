from fastapi.testclient import TestClient
from ..main import app
from fastapi import status

# checks 'healthy' endpoint in main
client = TestClient(app)
def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    # compares with the return statement from health_check() in main.py
    assert response.json() == {'status': 'healthy'}
