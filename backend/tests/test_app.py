import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_details_data(client):
    response = client.get('/api/sbom/test_product')
    assert response.status_code == 200
    data = response.get_json()
    assert 'sbomData' in data
    assert 'recData' in data

def test_get_versions(client):
    response = client.get('/get_versions?name=test_product')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_api_get_dependencies(client):
    response = client.get('/api/dependencies?name=test_product&version=1.0')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_api_get_dependencies_missing_params(client):
    response = client.get('/api/dependencies')
    assert response.status_code == 400
    data = response.get_json()
    assert 'description' in data
    assert data['description'] == "Missing required parameters: 'name' and 'version'"

