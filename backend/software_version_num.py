import requests
from urllib.parse import urljoin
import re
import json

url = "http://localhost:3030/kg/"

# Define the query
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

# Make the POST request with the query string
response = requests.post(url, data={"query": query})

# Check if the response was successful
if response.status_code == 200:
    print(f"Request successful: {response.text}")
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
            dependencies.append(dependency_uri)

    sbom = {
        "software_name": "aws-sdk-cpp",
        "software_version": "1.9.22",
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