import logging
from rdflib import Namespace
from models.ner_model import identify_entities
from models.relation_extraction_model import extract_relations
# import requests
import json
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SC = Namespace("https://w3id.org/secure-chain/")
SCHEMA = Namespace("http://schema.org/")

class SBOMService:
    def __init__(self, sparql_client):
        self.sparql_client = sparql_client
        logging.info("SBOMService initialized with SPARQL client.")

    def get_dependencies(self, software_name, software_version):
        query = f"""
        PREFIX sc: <https://w3id.org/secure-chain/>
        PREFIX schema: <http://schema.org/>

        SELECT ?dependency
        WHERE {{
            ?software a sc:Software .
            ?software schema:name "{software_name}" .
            ?software sc:hasSoftwareVersion ?softwareVersion .
            ?softwareVersion sc:versionName "{software_version}" .
            ?softwareVersion sc:dependsOn ?dependency .
        }}
        """
        logging.debug(f"Generated query: {query}")
        logging.debug(f"Querying dependencies for \"{software_name}\" version \"{software_version}\"")
        try:
            results = self.sparql_client.query(query)
            if results and 'results' in results and 'bindings' in results['results']:
                dependencies = []
                for binding in results['results']['bindings']:
                    dependency_url = binding['dependency']['value']
                    match = re.findall(r'[^/]+$', dependency_url)  # Extract the last part of the URL
                    if match:
                        dependencies.append(match[0])
                logging.debug(f"Dependencies found: {dependencies}")
                return dependencies
            else:
                logging.debug("No dependencies found.")
                return []
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return []

    def get_vulnerabilities(self, software_name, software_version):
        query = f"""
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
        logging.debug(f"Generated query: {query}")
        logging.debug(f"Querying vulnerabilities for \"{software_name}\" version \"{software_version}\"")
        try:
            results = self.sparql_client.query(query)
            if results and 'results' in results and 'bindings' in results['results']:
                vulnerabilities = [binding['vulnerability']['value'] for binding in results['results']['bindings']]
                logging.debug(f"Vulnerabilities found: {vulnerabilities}")
                return vulnerabilities
            else:
                logging.debug("No vulnerabilities found.")
                return []
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return []

    def get_sbom(self, software_name, software_version):
        try:
            logging.info(f"Generating SBOM for {software_name} version {software_version}")
            dependencies = self.get_dependencies(software_name, software_version)
            vulnerabilities = self.get_vulnerabilities(software_name, software_version)
            sbom2 = self.get_sbom_2(software_name, software_version)
            
            # Sbom out of the get_sbom_2 function
            # sbom = {
            #     "sbom": sbom2,
            # }

            # Sbom out of the dependencies and vulnerabilities functions
            sbom = {    
                'software': software_name,
                'version': software_version,
                'dependencies': dependencies,
                'vulnerabilities': vulnerabilities,
            }

            return json.dumps(sbom)
        except Exception as e:
            logging.error(f"Error generating SBOM: {e}", exc_info=True)
            return {}


    def get_sbom_2(self, software_name, software_version):
        try:
            logging.info("Generationo SBOM for {software_name} version {software_version}")
            query = f"""
            PREFIX sc: <https://w3id.org/secure-chain/>
            PREFIX schema: <http://schema.org/>

            SELECT ?software ?softwareVersion ?vulnerability 
            WHERE {{
                # Main software entity
                ?software a sc:Software;
                        schema:name "{software_name}".

                # Software as a SoftwareApplication
                OPTIONAL {{ ?software a schema:SoftwareApplication. }}
                
                ?softwareVersion sc:versionName "{software_version}".
                
                # Software to SoftwareVersion relationship
                OPTIONAL {{ ?software sc:hasSoftwareVersion ?softwareVersion. }}
                
                # SoftwareVersion back to Software (e.g., version of the software)
                OPTIONAL {{ ?softwareVersion sc:toSoftware ?relatedSoftwareVersion. }}

                # SoftwareVersion dependencies
                OPTIONAL {{ ?softwareVersion sc:dependsOn ?relatedSoftwareVersion. }}

                # SoftwareVersion is vulnerable to Vulnerabilities
                OPTIONAL {{ ?softwareVersion sc:vulnerableTo ?vulnerability. }}

                # Vulnerability types
                OPTIONAL {{ ?vulnerability sc:vulnerabilityType ?vulnerabilityType. }}
            }}
            LIMIT 100
            """

            results = self.sparql_client.query(query)
            if results and 'results' in results and 'bindings' in results['results']:
                sbom = []
                for binding in results['results']['bindings']:
                    sbom.append({
                        'software': binding['software']['value'],
                        'softwareVersion': binding['softwareVersion']['value'] if 'softwareVersion' in binding else None,
                        'relatedSoftwareVersion': binding['relatedSoftwareVersion']['value'] if 'relatedSoftwareVersion' in binding else None,
                        'vulnerability': binding['vulnerability']['value'] if 'vulnerability' in binding else None,
                        'vulnerabilityType': binding['vulnerabilityType']['value'] if 'vulnerabilityType' in binding else None
                    })
                logging.debug(f"SBOM generated: {sbom}")
                return sbom # Already tried to jsonfy it, but it didn't work
            else:
                logging.debug("No SBOM found.")
                return []
            
        except Exception as e:
            logging.error(f"Error generating SBOM: {e}", exc_info=True)
            return "Hey nothing here"

    def perform_ner(self, sbom):
        return identify_entities(sbom)

    def extract_relations(self, entities):
        return extract_relations(entities)
