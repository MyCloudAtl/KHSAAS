import logging
from rdflib import Namespace
from models.ner_model import identify_entities
from models.relation_extraction_model import extract_relations
import requests
import json
import re

#Configure logging
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
                    match = re.findall(r'[^/]+$', dependency_url) # Extract the last part of the URL
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
        logging.debug(f"Querying vulnerabilities for {software_name} version {software_version}")
        logging.debug(f"Generated vulnerabilities query: {query}")
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
            logging.error(f"Error executing vulnerabilities query: {e}")
            return []

    def get_sbom(self, software_name, software_version):
        try:
            logging.info(f"Generating SBOM for {software_name} version {software_version}")
            dependencies = self.get_dependencies(software_name, software_version)
            vulnerabilities = self.get_vulnerabilities(software_name, software_version)
            sbom = {
                'software': software_name,
                'version': software_version,
                'dependencies': dependencies,
                'vulnerabilities': vulnerabilities,
            }
            logging.debug(f"SBOM before enrichment: {sbom}")

            ner_results = self.perform_ner(sbom)
            logging.debug(f"NER results: {ner_results}")
            relation_results = self.extract_relations(ner_results)
            logging.debug(f"Relation extraction results: {relation_results}")
            sbom['enrichedData'] = relation_results

            return json.dumps(sbom)
        except Exception as e:
            logging.error(f"Error generating SBOM: {e}", exc_info=True)
            return {}

    # def perform_ner(self, sbom):
    #     return identify_entities(sbom)

    # def extract_relations(self, entities):
    #     return extract_relations(entities)
    def perform_ner(self, sbom):
        try:
            ner_results = identify_entities(sbom)
            logging.debug(f"NER results: {ner_results}")
            return ner_results
        except Exception as e:
            logging.error(f"Error performing NER: {e}")
            return []

    def extract_relations(self, entities):
        try:
            relation_results = extract_relations(entities)
            logging.debug(f"Relations extracted: {relation_results}")
            return relation_results
        except Exception as e:
            logging.error(f"Error extracting relations: {e}")
            return []
