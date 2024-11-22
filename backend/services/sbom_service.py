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
    
    def get_details(self, product_name):
        try:
            logging.info(f"Generating full SBOM for {product_name}")
            query = f"""
            PREFIX sc: <https://w3id.org/secure-chain/>
            PREFIX schema: <http://schema.org/>

            SELECT ?version ?dependency ?cve
            WHERE {{
                ?lib schema:name "{product_name}" .
                ?lib sc:hasSoftwareVersion ?version .
                ?dependency sc:dependsOn ?version .
                ?dependency sc:vulnerableTo ?cve .
            }}  
            """
            logging.debug(f"Generated query: {query}")
            results = self.sparql_client.query(query)
            if results and 'results' in results and 'bindings' in results['results']:
                sbom_data = []
                for binding in results['results']['bindings']:
                    # logging.info(binding['softwareVersion']['value'].split('/')[-1])
                    sbom_data.append({
                        'dependency': binding['dependency']['value'].split('/')[-1] if 'dependency' in binding else None,
                        'softwareVersion': binding['version']['value'].split('/')[-1] if 'version' in binding else None,
                        'vulnerability': binding['cve']['value'].split('/')[-1] if 'cve' in binding else None,
                    })
                # logging.debug(f"Bindings: {results.get('results', {}).get('bindings', [])}")
                return sbom_data
            else:
                logging.debug("No SBOM found.")
                return []

        except Exception as e:
            logging.error(f"Error generating SBOM: {e}", exc_info=True)
            return "Hey nothing here"


    # def get_sbom(self, software_name, software_version):
    #     try:
    #         logging.info(f"Generating SBOM for {software_name} version {software_version}")
    #         dependencies = self.get_dependencies(software_name, software_version)
    #         vulnerabilities = self.get_vulnerabilities(software_name, software_version)
    #         sbom = {
    #             'software': software_name,
    #             'version': software_version,
    #             'dependencies': dependencies,
    #             # 'vulnerabilities': vulnerabilities,
    #         }
    #         return sbom
    #     except Exception as e:
    #         logging.error(f"Error generating SBOM: {e}", exc_info=True)
    #         return {}

    def build_dashboard(self, software_name):
        # Ensure that the fetch functions are correctly imported
        from models.build_relationship_df import fetch_dependency_counts, fetch_vulnerability_counts, build_dataframe

        dependency_counts = fetch_dependency_counts(self.sparql_client, software_name)
        vulnerability_counts = fetch_vulnerability_counts(self.sparql_client, software_name)
        df = build_dataframe(dependency_counts, vulnerability_counts, software_name)
        return df