import logging
from rdflib import Namespace
from rdflib.plugins.sparql import prepareQuery
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, FOAF
from models.build_relationship_df import fetch_dependency_counts, fetch_vulnerability_counts, build_dataframe
import requests
import json
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SC = Namespace("https://w3id.org/secure-chain/")
SCHEMA = Namespace("http://schema.org/")

class SBOMService:
    def __init__(self, sparql_client):
        self.sparql_client = sparql_client
        self.dependency_regex_patterns = [
            (r".*/([^/#]+)#(\d+)", r"\1 \2"),  
            (r".*/([^/#]+)#%2A", r"\1 *"),    
            (r".*/([^/#]+)#(.+)", r"\1 \2"),  
        ]
        self.vulnerability_regex_patterns = [
            (r".*/([^/]*)$", r"\1"),
        ]
        logging.info("SBOMService initialized with SPARQL client.")

    def format_dependency(self, uri):
        # Apply each regex pattern to the dependency URI
        for pattern, replacement in self.dependency_regex_patterns:
            uri = re.sub(pattern, replacement, uri)
        return unquote(uri)  

    def format_vulnerability(self, uri):
        # Apply each regex pattern to the vulnerability URI
        for pattern, replacement in self.vulnerability_regex_patterns:
            uri = re.sub(pattern, replacement, uri)
        return unquote(uri)  

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
                    formatted_dependency = self.format_dependency(dependency_uri)
                    dependencies.append(formatted_dependency)
                if dependencies:
                    logging.debug(f"Dependencies found: {dependencies}")
                    return dependencies
            else:
                logging.debug("No dependencies found.")
                return ["No dependencies found."]
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return ["No dependencies found."]

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
            vulnerabilities = []
            if results and 'results' in results and 'bindings' in results['results']:
                for binding in results['results']['bindings']:
                    vulnerability_uri = binding['vulnerability']['value']
                    formatted_vulnerability = self.format_vulnerability(vulnerability_uri)
                    vulnerabilities.append(formatted_vulnerability)
                if vulnerabilities:
                    logging.debug(f"Vulnerabilities found: {vulnerabilities}")
                    return vulnerabilities
        except Exception as e:
            logging.error(f"Error executing vulnerabilities query: {e}")
            return ["No vulnerabilities found."]
    
    def get_full_sbom(self, software_name, software_version, limit=100):
        try:
            logging.info(f"Generating full SBOM for {software_name} version {software_version}")
            query = f"""
            PREFIX sc: <https://w3id.org/secure-chain/>
            PREFIX schema: <http://schema.org/>

            SELECT ?software ?softwareVersion ?vulnerability ?vulnerabilityType ?hardware ?hardwareVersion ?license ?manufacturer ?organization ?person
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
            results = self.sparql_client.query(query)
            if results and 'results' in results and 'bindings' in results['results']:
                sbom_data = []
                for binding in results['results']['bindings']:
                    sbom_data.append({
                        'software': binding['software']['value'].split('/')[-1],
                        'softwareVersion': binding['softwareVersion']['value'].split('/')[-1] if 'softwareVersion' in binding else None,
                        'vulnerability': binding['vulnerability']['value'].split('/')[-1] if 'vulnerability' in binding else None,
                        'vulnerabilityType': binding['vulnerabilityType']['value'].split('/')[-1] if 'vulnerabilityType' in binding else None,
                        'hardware': binding['hardware']['value'].split('/')[-1] if 'hardware' in binding else None,
                        'hardwareVersion': binding['hardwareVersion']['value'].split('/')[-1] if 'hardwareVersion' in binding else None,
                        'license': binding['license']['value'].split('/')[-1] if 'license' in binding else None,
                        'manufacturer': binding['manufacturer']['value'].split('/')[-1] if 'manufacturer' in binding else None,
                        'organization': binding['organization']['value'].split('/')[-1] if 'organization' in binding else None,
                        'person': binding['person']['value'].split('/')[-1] if 'person' in binding else None
                    })
                logging.debug(f"SBOM generated: {sbom_data}")
                return sbom_data
            else:
                logging.debug("No SBOM found.")
                return []

        except Exception as e:
            logging.error(f"Error generating SBOM: {e}", exc_info=True)
            return "Hey nothing here"

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
            return sbom
        except Exception as e:
            logging.error(f"Error generating SBOM: {e}", exc_info=True)
            return {}

    def build_dashboard(self, software_name):
        # Ensure that the fetch functions are correctly imported
        from models.build_relationship_df import fetch_dependency_counts, fetch_vulnerability_counts, build_dataframe

        dependency_counts = fetch_dependency_counts(self.sparql_client, software_name)
        vulnerability_counts = fetch_vulnerability_counts(self.sparql_client, software_name)
        df = build_dataframe(dependency_counts, vulnerability_counts, software_name)
        return df