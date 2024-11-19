import logging
from rdflib import Namespace
from models.ner_model import identify_entities
from models.relation_extraction_model import extract_relations
import requests
import json
import re

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
                    match = re.findall(r'[^/]+$', dependency_url)  #Extract the last part of the URL
                    if match:
                        dependencies.append(match[0])
                logging.debug(f"Dependencies found: {dependencies}")
                return dependencies
            else:
                logging.debug("No dependencies found.")
                return ["No dependencies found."]
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return ["Error retrieving dependencies."]

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
                return ["No vulnerabilities found."]
        except Exception as e:
            logging.error(f"Error executing vulnerabilities query: {e}")
            return ["Error retrieving vulnerabilities."]
    
    def get_full_sbom(self, software_name, software_version, limit=10):
        query = f"""
        PREFIX sc: <https://w3id.org/secure-chain/>
        PREFIX schema: <http://schema.org/>

        SELECT DISTINCT ?software ?softwareApplication ?softwareVersion ?relatedSoftwareVersion
                        ?license ?vulnerability ?vulnerabilityType ?vulnerableSoftware 
                        ?hardwareVersion ?hardware ?organization ?person
                        ?dependency ?affiliation ?contributor ?manufacturer ?producer
        WHERE {{
          # Specify the software you are interested in
          ?lib schema:name "{software_name}" .
          ?lib sc:hasSoftwareVersion ?softwareVersion .
          ?softwareVersion sc:versionName "{software_version}" .

          # Main software entity
          ?software a sc:Software.

          # Software as a SoftwareApplication (optional)
          OPTIONAL {{ ?software a schema:SoftwareApplication. }}

          # SoftwareVersion relationships
          OPTIONAL {{ ?software sc:hasSoftwareVersion ?softwareVersion. }}
          OPTIONAL {{ ?softwareVersion sc:toSoftware ?relatedSoftwareVersion. }}
          OPTIONAL {{ ?softwareVersion sc:dependsOn ?dependency. }}

          # License and related licenses (optional)
          OPTIONAL {{ ?softwareVersion sc:license ?license. }}
          OPTIONAL {{ ?license a schema:CreativeWork. }}

          # Hardware relationships
          OPTIONAL {{ ?softwareVersion sc:OperatesOn ?hardwareVersion. }}
          OPTIONAL {{ ?hardwareVersion a sc:HardwareVersion. }}
          OPTIONAL {{ ?hardwareVersion sc:toHardware ?hardware. }}
          OPTIONAL {{ ?hardware a schema:Product. }}

          # Vulnerabilities and related information
          OPTIONAL {{ ?softwareVersion sc:vulnerableTo ?vulnerability. }}
          OPTIONAL {{ ?vulnerability sc:vulnerabilityType ?vulnerabilityType. }}
          OPTIONAL {{ ?vulnerabilityType a schema:Intangible. }}

          # Discovered by organizations and people
          OPTIONAL {{ ?vulnerability sc:discoveredBy ?organization. }}
          OPTIONAL {{ ?organization a schema:Organization. }}
          OPTIONAL {{ ?vulnerability sc:discoveredBy ?person. }}
          OPTIONAL {{ ?person a schema:Person. }}

          # Affiliation and contributor relations
          OPTIONAL {{ ?person schema:affiliation ?organization. }}
          OPTIONAL {{ ?softwareVersion schema:contributor ?person. }}

          # Manufacturer and producer details
          OPTIONAL {{ ?hardware schema:manufacturer ?manufacturer. }}
          OPTIONAL {{ ?hardware schema:producer ?producer. }}
        }}  
        """

        if isinstance(limit, int) and limit > 0:
            query += f" LIMIT {limit}"

        logging.debug(f"Generated query with limit {limit}: {query}")
        try:
            results = self.sparql_client.query(query)
            if results and 'results' in results and 'bindings' in results['results']:
                sbom_data = []
                for binding in results['results']['bindings']:
                    sbom_data.append({
                        'software': binding.get('software', {}).get('value', ''),
                        # 'softwareApplication': binding.get('softwareApplication', {}).get('value', ''),
                        'softwareVersion': binding.get('softwareVersion', {}).get('value', ''),
                        # 'relatedSoftwareVersion': binding.get('relatedSoftwareVersion', {}).get('value', ''),
                        'license': binding.get('license', {}).get('value', ''),
                        'vulnerability': binding.get('vulnerability', {}).get('value', ''),
                        'vulnerabilityType': binding.get('vulnerabilityType', {}).get('value', ''),
                        # 'vulnerableSoftware': binding.get('vulnerableSoftware', {}).get('value', ''),
                        'hardwareVersion': binding.get('hardwareVersion', {}).get('value', ''),
                        'hardware': binding.get('hardware', {}).get('value', ''),
                        'organization': binding.get('organization', {}).get('value', ''),
                        'person': binding.get('person', {}).get('value', ''),
                        # 'dependency': binding.get('dependency', {}).get('value', ''),
                        'manufacturer': binding.get('manufacturer', {}).get('value', ''),
                    })
                logging.debug(f"SBOM data retrieved with limit {limit}: {sbom_data}")
                return sbom_data
            else:
                logging.debug("No results found.")
                return {"message": "No data found."}
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return {"error": "Error retrieving SBOM data."}

    def get_sbom(self, software_name, software_version):
        try:
            logging.info(f"Generating SBOM for {software_name} version {software_version}")
            dependencies = self.get_dependencies(software_name, software_version)
            vulnerabilities = self.get_vulnerabilities(software_name, software_version)
            licenses = self.get_licenses(software_name, software_version)
            sbom = {
                'software': software_name,
                'version': software_version,
                'dependencies': dependencies,
                'vulnerabilities': vulnerabilities,
                'licenses': licenses
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
