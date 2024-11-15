from rdflib import Namespace
from services.ner_service import identify_entities
from services.relation_extraction_service import extract_relations

SC = Namespace("https://w3id.org/secure-chain/")
SCHEMA = Namespace("http://schema.org/")

class SBOMService:
    def __init__(self, sparql_client):
        self.sparql_client = sparql_client
    
    def get_dependencies(self, software_name, software_version):
        # Aquí va la lógica para obtener las dependencias
        dependencies_query = f"""
        PREFIX sc: <https://w3id.org/secure-chain/>
        PREFIX schema: <http://schema.org/>
        SELECT ?dependency 
        WHERE {{
        ?software a sc:Software .
        ?software schema:name {software_name} .
        ?software sc:hasSoftwareVersion ?softwareVersion .
        ?softwareVersion sc:versionName {software_version} .
        ?softwareVersion sc:dependsOn ?dependency .
        ?dependency sc:hasSoftwareVersion ?dependencyVersion .
        ?dependencyVersion sc:versionName ?dependencyVersionName
        }}
        """

        print("Dependencies Query:", dependencies_query)
        dependencies_response = self.sparql_client.query(dependencies_query)

        # if not isinstance(dependencies_response, list):
        #     return []
        return [str(row['dependency']) for row in dependencies_response]
    
    def get_vulnerabilities(self, software_name, software_version):

        # Aquí va la lógica para obtener las vulnerabilidades
        vulnerabilities_query = f"""
        PREFIX sc: <https://w3id.org/secure-chain/>
        PREFIX schema: <http://schema.org/>

        SELECT ?vulnerability
        WHERE {{
            ?software a sc:Software .
            ?software schema:name "{software_name}" .
            ?software sc:hasSoftwareVersion ?softwareVersion .
            ?softwareVersion sc:versionName "{software_version}" .
            ?softwareVersion sc:vulnerableTo ?vulnerability .
        }}
        """
        
        vulnerabilities_response = self.sparql_client.query(vulnerabilities_query)
        
        # By the moment, we are not recieving any vulnerabilities
        # so we return an empty list
        if not isinstance(vulnerabilities_response, list):
            return []
        return [str(row['vulnerability']) for row in vulnerabilities_response]
    
    def get_sbom(self, software_name, software_version):
        sbom = {
            'software': software_name,
            'version': software_version,
            'dependencies': self.get_dependencies(software_name, software_version),
            # 'vulnerabilities': self.get_vulnerabilities(software_name, software_version)
        }

        # Utilizar NER y extracción de relaciones para enriquecer el SBOM
        # ner_results = identify_entities(sbom)
        # relation_results = extract_relations(ner_results)
        # sbom['enrichedData'] = relation_results

        return sbom