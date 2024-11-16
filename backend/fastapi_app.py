from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from utils.sparql_client import SPARQLClient
from services.sbom_service import SBOMService 

# Configuration for SPARQL endpoints
SPARQL_ENDPOINT_URL = 'http://localhost:3030/kg/'
SPARQL_UPDATE_ENDPOINT_URL = 'http://localhost:3030/dataset/update'

app = FastAPI()

# Define a function to provide a SPARQL client instance
def get_sparql_client():
    return SPARQLClient(SPARQL_ENDPOINT_URL, SPARQL_UPDATE_ENDPOINT_URL)

# Service class using the SPARQL client
class SBOMService:
    def __init__(self, sparql_client: SPARQLClient):
        self.sparql_client = sparql_client

# Dependency that provides SBOMService
def get_sbom_service(sparql_client: SPARQLClient = Depends(get_sparql_client)):
    return SBOMService(sparql_client)

class SoftwareQuery(BaseModel):
    name: str
    version: str

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/api/dependencies")
async def api_get_dependencies(query: SoftwareQuery, sbom_service: SBOMService = Depends(get_sbom_service)):
    dependencies = sbom_service.get_dependencies(query.name, query.version)
    return {"name": query.name, "version": query.version, "dependencies": dependencies}

@app.get("/api/vulnerabilities")
async def api_get_vulnerabilities(query: SoftwareQuery, sbom_service: SBOMService = Depends(get_sbom_service)):
    vulnerabilities = sbom_service.get_vulnerabilities(query.name, query.version)
    return {"name": query.name, "version": query.version, "vulnerabilities": vulnerabilities}

@app.get("/api/sbom")
async def api_get_sbom(query: SoftwareQuery, sbom_service: SBOMService = Depends(get_sbom_service)):
    sbom = sbom_service.get_sbom(query.name, query.version)
    return {"name": query.name, "version": query.version, "sbom": sbom}