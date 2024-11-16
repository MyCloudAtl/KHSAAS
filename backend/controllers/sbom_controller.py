from flask import request, jsonify
from services.sbom_service import SBOMService
from utils.sparql_client import SPARQLClient

# Initialize the SBOM service with the SPARQL client
sbom_service = SBOMService(SPARQLClient('http://localhost:3030/kg/', 'http://localhost:3030/dataset/update'))

def get_sbom_controller():
    # Retrieve parameters from query string instead of request body
    software_name = request.args.get('software_name')
    software_version = request.args.get('software_version')
    
    # Check for the presence of required parameters
    if not software_name or not software_version:
        return jsonify({"error": "Missing required parameters"}), 400

    # Retrieve the SBOM using the service
    sbom = sbom_service.get_sbom(software_name, software_version)
    return jsonify(sbom)
