import logging
import json
import re
from urllib.parse import unquote
from rdflib import Namespace
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, request, render_template, jsonify, abort
from utils.sparql_client import SPARQLClient
from urllib.parse import unquote
from routes.sbom_routes import sbom_bp
from services.sbom_service import SBOMService 
from utils.data_loader import load_products
from flask_cors import CORS
from llm.intent import handle_intent, SoftwareQuery
import os
import langchainIntegration 
# Load the products from the CSV
products_df = load_products('data/products_versions.csv').drop_duplicates(subset=['product', 'version'])
# products_df2 = products_df.iloc[0:1000]
grouped_products = products_df.groupby('product')['version'].apply(list).to_dict()

app = Flask(__name__)
CORS(app)

# Read environment variables from .env file
base_url = os.getenv('BASE_URL', 'http://localhost:3030')

# Existing SPARQL client setup
SPARQL_ENDPOINT_URL = base_url + '/kg/'
SPARQL_UPDATE_ENDPOINT_URL = base_url + '/kg/update'
print(f"SPARQL endpoint is {SPARQL_ENDPOINT_URL}")

sparql_client = SPARQLClient(SPARQL_ENDPOINT_URL, SPARQL_UPDATE_ENDPOINT_URL)
app.config['sparql_client'] = sparql_client

if sparql_client.test_connection():
    print("Connection to SPARQL endpoint successful.")
else:
    print("Connection to SPARQL endpoint failed.")

# Register blueprints
app.register_blueprint(sbom_bp, url_prefix='/sbom')

# Initialize SBOMService with the SPARQL client
sbom_service = SBOMService(sparql_client)

@app.route('/')
def home():
    return render_template('index.html', products=grouped_products)

# @app.route('/api/softwares', methods=['GET'])
# def get_softwares():
#     return jsonify(grouped_products)

# @app.route('/api/softwares/<software_name>/versions', methods=['GET'])
# def get_versions_for_software(software_name):
#     versions = grouped_products.get(software_name, [])
#     return jsonify(versions)

# @app.route('/api/sbom/<software_name>/<software_version>', methods=['GET'])
# def get_sbom(software_name, software_version):
#     try:
#         sbom_data = sbom_service.get_full_sbom(software_name, software_version)
#         return jsonify(sbom_data)
#         # if sbom_data:
#         #     return jsonify(json.loads(sbom_data))
#         # else:
#         #     return jsonify({"error": "Unable to generate SBOM"}), 500
#     except Exception as e:
#         logging.error(f"Error generating SBOM: {e}")
#         return jsonify({"error": "Unable to generate SBOM"}), 500

@app.route('/api/sbom/<product_name>', methods=['GET'])
def get_details_data(product_name):
    product_name = unquote(product_name).lower()  # Decode the URL parameter
    app.logger.info(f"Decoded product name: {product_name}")  # Log the decoded product name
    try:
        sbom_data = sbom_service.get_details(product_name)
        rec_data = sbom_service.get_recommendation(product_name)
        if not sbom_data:
            return jsonify({"error": "SBOM data not found for the specified product"}), 404
        return jsonify({ 'sbomData': sbom_data,
            'recData': rec_data})
    except Exception as e:
        app.logger.error(f"Error fetching SBOM data for {product_name}: {e}")
        return jsonify({"error": "Failed to fetch SBOM data"}), 500

@app.route('/get_versions', methods=['GET'])
def get_versions():
    product_name = request.args.get('name', '')
    versions = grouped_products.get(product_name, [])  # Get versions for the selected product
    return jsonify(versions)

@app.route('/api/dependencies', methods=['GET'])
def api_get_dependencies():
    software_name = request.args.get('name')
    software_version = request.args.get('version')
    if not software_name or not software_version:
        abort(400, description="Missing required parameters: 'name' and 'version'")
    dependencies = sbom_service.get_dependencies(software_name, software_version)
    return jsonify(dependencies)

@app.route('/api/vulnerabilities', methods=['GET'])
def api_get_vulnerabilities():
    software_name = request.args.get('name')
    software_version = request.args.get('version')
    vulnerabilities = sbom_service.get_vulnerabilities(software_name, software_version)
    return jsonify(vulnerabilities)

@app.route('/api/sbom', methods=['POST'])
def api_post_sbom():
    data = request.get_json()
    software_name = request.args.get('name')
    software_version = request.args.get('version')
    if not software_name or not software_version:
        return jsonify({"error": "Missing required parameters"}), 400
    try:
    # Generate the SBOM using the provided software name and version
        sbom = sbom_service.get_sbom(software_name, software_version)
        return jsonify(sbom)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sbom', methods=['GET'])
def get_sbom_controller():
    # Retrieve parameters from query string instead of request body
    software_name = request.args.get('software_name')
    software_version = request.args.get('software_version')
    
    # Check for the presence of required parameters
    if not software_name or not software_version:
        return jsonify({"error": "Missing required parameters: 'software_name' and 'software_version'"}), 400

    try:
        # Retrieve the SBOM using the service
        sbom = sbom_service.get_sbom(software_name, software_version)
        return jsonify(sbom)
    except Exception as e:
        logging.error(f"Error retrieving SBOM: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while retrieving the SBOM."}), 500

@app.route('/api/chat', methods=['POST'])
def api_post_chat():
    data = request.get_json()
    user_query = data.get('query')
    
    response = handle_intent(user_query)
    return jsonify(response)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    software_name = request.args.get('software_name')
    if not software_name or not is_valid_software_name(software_name):
        return jsonify({'error': 'A valid software_name parameter is required'}), 400
    try:
        # Build the dashboard DataFrame
        df = sbom_service.build_dashboard(software_name)
        # Convert the DataFrame to JSON
        dashboard_data = df.to_dict(orient='records')
        return jsonify(dashboard_data)
    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500

@app.route('/get_intent', methods=['POST'])
def get_intent():
    # Check if request contains JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
    data = request.json
    user_input = data.get("query", "")
    print("174:", user_input)
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    try:
        result = langchainIntegration.fetchIntent(user_input)
        print(result)
        return result
    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500


# Function to generate and process SPARQL query from user input.
@app.route('/process_query', methods=['POST'])
def process_query():
    # Check if request contains JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.json
    user_input = data.get("query", "")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    try:
        query_para = langchainIntegration.process_userinput(user_input)
        print("line 200:", query_para)
        software_name = query_para["SoftwareName"]
        version = query_para["Version"]
        if query_para["type"] =="dependencies":
            print("line204:")
            sparql_result =sbom_service.get_dependencies(software_name ,version)
            print("result on line 206: ", sparql_result)
            if sparql_result is None:
                return jsonify({"sparql_result":"No Dependencies found for specified software." })
            return jsonify({"sparql_result":sparql_result})
        elif query_para["type"] =="vulnerabilities":
            sparql_result =sbom_service.get_vulnerabilities(software_name ,version)
            print("result on line 206: ", sparql_result)
            if sparql_result is None:
                return jsonify({"sparql_result":"No Vulnerabilities found for specified software. "})
            return jsonify({"sparql_result":sparql_result})
    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)
