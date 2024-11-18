from flask import Flask, request, render_template, jsonify, abort
from utils.sparql_client import SPARQLClient
from routes.sbom_routes import sbom_bp
from services.sbom_service import SBOMService 
from utils.data_loader import load_products
from flask_cors import CORS

# Load the products from the CSV
products_df = load_products('data/products_versions.csv').drop_duplicates(subset=['product', 'version'])
products_df2 = products_df.iloc[0:1000]
grouped_products = products_df2.groupby('product')['version'].apply(list).to_dict()

app = Flask(__name__)
CORS(app)

# Existing SPARQL client setup
SPARQL_ENDPOINT_URL = 'http://localhost:3030/kg'
SPARQL_UPDATE_ENDPOINT_URL = 'http://localhost:3030/kg/update'
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

@app.route('/api/softwares', methods=['GET'])
def get_softwares():
    return jsonify(grouped_products)

@app.route('/api/softwares/<software_name>/versions', methods=['GET'])
def get_versions_for_software(software_name):
    versions = grouped_products.get(software_name, [])
    return jsonify(versions)


@app.route('/api/sbom/<software_name>/<software_version>', methods=['GET'])
def get_sbom(software_name, software_version):
    # Generate the SBOM using the provided software name and version
    sbom = sbom_service.get_sbom(software_name, software_version)
    return jsonify(sbom)


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
if __name__ == '__main__':
    app.run(debug=True)