import pytest
from unittest.mock import MagicMock
from services.sbom_service import SBOMService


# Define the sbom_service fixture to create an instance of SBOMService
# and a mock SPARQL client
@pytest.fixture
def sbom_service():
    mock_sparql_client = MagicMock()
    return SBOMService(mock_sparql_client), mock_sparql_client

# Test case for get_full_sbom method with results
def test_get_full_sbom_with_results(sbom_service):
    sbom_service_instance, mock_sparql_client = sbom_service

    # Mock the SPARQL client query response
    mock_sparql_client.query.return_value = {
        'results': {
            'bindings': [
                {
                    'software': {'value': 'http://example.com/software/1'},
                    'softwareVersion': {'value': 'http://example.com/softwareVersion/1.0'},
                    'vulnerability': {'value': 'http://example.com/vulnerability/1'},
                    'vulnerabilityType': {'value': 'http://example.com/vulnerabilityType/1'},
                    'hardware': {'value': 'http://example.com/hardware/1'},
                    'hardwareVersion': {'value': 'http://example.com/hardwareVersion/1.0'},
                    'license': {'value': 'http://example.com/license/1'},
                    'manufacturer': {'value': 'http://example.com/manufacturer/1'},
                    'organization': {'value': 'http://example.com/organization/1'},
                    'person': {'value': 'http://example.com/person/1'}
                }
            ]
        }
    }

    result = sbom_service_instance.get_full_sbom('TestSoftware', '1.0')
    expected_result = [{
        'software': '1',
        'softwareVersion': '1.0',
        'vulnerability': '1',
        'vulnerabilityType': '1',
        'hardware': '1',
        'hardwareVersion': '1.0',
        'license': '1',
        'manufacturer': '1',
        'organization': '1',
        'person': '1'
    }]
    assert result == expected_result


# Test case for get_full_sbom method with no results
def test_get_full_sbom_no_results(sbom_service):
    sbom_service_instance, mock_sparql_client = sbom_service

    # Mock the SPARQL client query response with no results
    mock_sparql_client.query.return_value = {
        'results': {
            'bindings': []
        }
    }

    result = sbom_service_instance.get_full_sbom('TestSoftware', '1.0')
    expected_result = []
    assert result == expected_result

# Test case for get_full_sbom method with exception
def test_get_full_sbom_query_exception(sbom_service):
    sbom_service_instance, mock_sparql_client = sbom_service

    # Mock the SPARQL client to raise an exception
    mock_sparql_client.query.side_effect = Exception("Query error")

    result = sbom_service_instance.get_full_sbom('TestSoftware', '1.0')
    expected_result = "Hey nothing here"
    assert result == expected_result
