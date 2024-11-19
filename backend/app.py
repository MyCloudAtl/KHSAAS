from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from utils.sparql_client import SPARQLClient
from routes.sbom_routes import sbom_bp
from services.sbom_service import SBOMService 
from utils.data_loader import load_products
import re

# Load the products from the CSV
products_df = load_products('data/products_versions.csv').drop_duplicates(subset=['product', 'version'])
products_df2 = products_df.iloc[0:1000]
grouped_products = products_df2.groupby('product')['version'].apply(list).to_dict()

app = Flask(__name__)
CORS(app)

# Existing SPARQL client setup
SPARQL_ENDPOINT_URL = 'http://localhost:3030/kg/query'
SPARQL_UPDATE_ENDPOINT_URL = 'http://localhost:3030/kg/update'
sparql_client = SPARQLClient(SPARQL_ENDPOINT_URL, SPARQL_UPDATE_ENDPOINT_URL)
app.config['sparql_client'] = sparql_client

# Register blueprints
app.register_blueprint(sbom_bp, url_prefix='/sbom')

# Initialize SBOMService with the SPARQL client
sbom_service = SBOMService(sparql_client)

def is_valid_software_name(name):
    # Simple regex to allow alphanumeric and spaces
    return re.match(r'^[\w\s]+$', name) is not None

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

@app.route('/')
def home():
    return render_template('index.html', products=grouped_products)

@app.route('/get_versions', methods=['GET'])
def get_versions():
    # Retrieve product name from query parameters
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
def api_get_sbom():
    data = request.get_json()
    software_name = data.get('name')
    software_version = data.get('version')
    if not software_name or not software_version:
        return jsonify({"error": "Missing required parameters"}), 400

    # Generate the SBOM using the provided software name and version
    sbom = sbom_service.get_sbom(software_name, software_version)
    return jsonify(sbom)

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

if __name__ == '__main__':
    app.run(debug=True)