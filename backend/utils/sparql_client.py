from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLClient:
    def __init__(self, endpoint_url, update_endpoint_url):
        self.endpoint_url = endpoint_url
        self.update_endpoint_url = update_endpoint_url
        # Aqui nos conectamos a la base de datos
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)

    def query(self, query_string):
        self.sparql.setQuery(query_string)
        try:
            results = self.sparql.query().convert()
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            return None