import requests
from urllib.parse import urljoin
import re
import json

url = "http://localhost:3030/kg/"

def dependencies_query(): 
    query = """
    PREFIX sc: <https://w3id.org/secure-chain/>
    PREFIX schema: <http://schema.org/>

    SELECT ?dependency 

    WHERE {
        ?software a sc:Software .
        ?software schema:name "aws-sdk-cpp" .
        ?software sc:hasSoftwareVersion ?softwareVersion .
        ?softwareVersion sc:versionName ?versionName .
        ?softwareVersion a sc:SoftwareVersion .
        ?softwareVersion sc:versionName "1.9.22" .
        ?softwareVersion sc:dependsOn ?dependency .
    }
    """
    return query

def send_query(query):
    headers = {
        'Content-Type': 'application/sparql-query',
        'Accept': 'application/sparql-results+json'
    }
    response = requests.post(url, data=query, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return None

def vulnerabilities_query():
    query = """ """ # Add the SPARQL query here

    return query


dependency_query = dependencies_query()
vulnerability_query = vulnerabilities_query()
# Make the POST request with the query string
response = requests.post(url, data={"query": dependencies_query})
response = requests.post(url, data={"query": vulnerability_query})


# Check if the response was successful
if response.status_code == 200:
    print(f"Request successful: {response.status_code}")
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")

try:
    data = json.loads(response.text)
    dependencies = []
    for result in data['results']['bindings']:
        dependency_uri = result['dependency']['value']
        match = re.findall(r'\d+(?:\.\d+)+', dependency_uri)
        if match:
            dependencies.extend(match)
        else:
            dependencies.append(dependency_uri.split('/')[-1])

    sbom = {
        "software_name": "aws-sdk-cpp",
        "software_version": "1.9.376",
        "dependencies": dependencies
    }

    # Convert the SBOM dictionary to a JSON string
    sbom_json = json.dumps(sbom, indent=4)

    # Save the JSON string to a file
    with open("sbom.json", "w") as file:
        file.write(sbom_json)

    print("SBOM saved to sbom.json")
    print(sbom_json)
except (json.JSONDecodeError, KeyError) as e:
    print(f"Error processing JSON response: {e}")
    print(f"Response text was: {response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")