from flask import Flask
from utils.sparql_client import SPARQLClient
from routes.sbom_routes import sbom_bp

app = Flask(__name__)

# Configuración del cliente SPARQL
SPARQL_ENDPOINT_URL = 'http://localhost:3030/kg/'
SPARQL_UPDATE_ENDPOINT_URL = 'http://localhost:3030/dataset/update'
sparql_client = SPARQLClient(SPARQL_ENDPOINT_URL, SPARQL_UPDATE_ENDPOINT_URL)

# Registrar blueprints y pasar el cliente SPARQL
app.register_blueprint(sbom_bp, url_prefix='/sbom')
app.config['sparql_client'] = sparql_client

if __name__ == '__main__':
    app.run(debug=True)