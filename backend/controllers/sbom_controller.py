from flask import request, jsonify
from services.sbom_service import SBOMService
from utils.sparql_client import SPARQLClient

sbom_service =SBOMService(SPARQLClient('http://localhost:3030/kg/', 'http://localhost:3030/dataset/update'))

def get_sbom_controller():
    data = request.get_json()
    software_name = data.get('software_name')
    software_version = data.get('software_version')
    
    if not software_name or not software_version:
        return jsonify({"error": "Missing required parameters"}), 400

    sbom = sbom_service.get_sbom()
    return jsonify(sbom)

    