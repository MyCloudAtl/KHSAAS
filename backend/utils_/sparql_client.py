from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

class SPARQLClient:
    def __init__(self, endpoint_url, update_endpoint_url):
        self.endpoint_url = endpoint_url
        self.update_endpoint_url = update_endpoint_url
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)
        logging.debug(f"SPARQLClient initialized with endpoint: {endpoint_url}")

    def query(self, query_string):
        self.sparql.setQuery(query_string)
        try:
            results = self.sparql.query().convert()
            return results
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return None

    def test_connection(self):
        test_query = "ASK WHERE { ?s ?p ?o }"
        self.sparql.setQuery(test_query)
        try:
            self.sparql.query().convert()
            logging.debug("Connection to SPARQL endpoint successful.")
            return True
        except Exception as e:
            logging.error(f"Error connecting to SPARQL endpoint: {e}")
            return False