import requests
from urllib.parse import urljoin

import re
# Define the URL and query parameters
# url = "http://34.200.228.166:3030/kg/"
# url = "http://localhost:4040/kg/"
url = "http://localhost:3030/kg/"

# Define the query
query = """
PREFIX sc: <https://w3id.org/secure-chain/>
PREFIX schema: <http://schema.org/>

SELECT ?softwareVersion ?dependency

WHERE {
?software a sc:Software .
?software schema:name "aws-sdk-cpp" .
?software sc:hasSoftwareVersion ?softwareVersion
}
"""

# Make the POST request with the query string
response = requests.post(url, data={"query": query})

# Check if the response was successful
if response.status_code == 200:
    print(f"Request successful: {response.text}")
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")

# GET /versions?software=aws-sdk-cpp
# ["1.13.0", "1.12.3"]

try:
    import json
    data = json.loads(response.text)
    versions = []
    for result in data['results']['bindings']:
        version_string = result['softwareVersion']['value']
        # Use regular expression to extract numbers
        match = re.findall(r'\d+(?:\.\d+)+', version_string)  # Matches one or more digits, followed by zero or more occurrences of ".digits"
        if match:
          versions.extend(match)

    print(versions)
except (json.JSONDecodeError, KeyError) as e:
    print(f"Error processing JSON response: {e}")
    print(f"Response text was: {response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")