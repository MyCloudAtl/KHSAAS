from flask import Flask, request, jsonify
from rdflib import Graph
from langchain.llms import OpenAI
import json

app = Flask(__name__)

# Load the Turtle file
graph = Graph()
graph.parse("securechain.ttl", format="ttl")

# Initialize the language model for generating SPARQL queries
llm = OpenAI(model="gpt-3.5-turbo" , openai_api_key="your_openai_api_key_here")

@app.route('/fetch-intent', methods=['POST'])
def fetchIntent():
    data = request.json
    user_input = data.get("query", "")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    prompt = f"Detect user intent for: {input}"
    user_intent = llm(prompt).strip()
     # Return the detected intent
    return jsonify({"intent": user_intent})

# Function to generate SPARQL query from user input
@app.route('/fetch-query', methods=['POST'])
def generate_sparql():
    data = request.json
    verified_intent = data.get("query","")
    if not verified_intent:
        return jsonify({"error": "No intent provided"}), 400
    prompt = f"Convert the following user input into a SPARQL query: {verified_intent}"
    sparql_query = llm(prompt).strip()
    return jsonify({"sparql":sparql_query})


#TODO - just  call execute query method in generate_sparql method after testing. No need to create a seperate end point
# Execute the SPARQL query if it's valid
@app.route('/execute-query', methods=['POST'])
def execute_query():
    sparql_query = request.json.get("query","")
    if sparql_query:
        try:
            results = graph.query(sparql_query)

            # Convert results to JSON
            results_json = [{"predicate": str(row.predicate), "object": str(row.object)} for row in results]

            # TODO: send results back to javascript frontend
            return jsonify({"results": results_json})

        except Exception as e:
            return jsonify({"error": f"Error executing SPARQL query: {e}"}), 500
    else:
        return jsonify({"error": "No query provided"}), 400

if __name__ == '__main__':
    app.run(port=3030)