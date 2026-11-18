from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_create_ticket():
    result = client.post('/tickets', json={'subject': 'Duplicate charge', 'message': 'I was charged twice this month.'})
    assert result.status_code == 201
    assert result.json()['status'] == 'new'
