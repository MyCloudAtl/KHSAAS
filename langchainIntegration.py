from flask import Flask, request, jsonify
from rdflib import Graph
#from langchain_community.llms import OpenAI
from langchain_huggingface import HuggingFaceEndpoint
import json
import os
import spacy
from spellchecker import SpellChecker
import re

app = Flask(__name__)

# Load the Turtle file
graph = Graph()
graph.parse("shortened_sc.ttl", format="ttl")

api_key = "iMllLsv1LhqGb-HaLebOQLevMu65uRQ6-qxblPBHaok_81fL1KYPphxAZjKOMA"
# Initialize the language model for generating SPARQL queries
#llm = OpenAI(model="gpt-3.5-turbo" , openai_api_key=api_key)

# Set your Hugging Face API token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
# Initialize the HuggingFace model
llm = HuggingFaceEndpoint(repo_id="gpt2", huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
nlp = spacy.load("en_core_web_sm")

#llm = Ollama(model="llama2")

@app.route('/get_intent', methods=['POST'])
def fetchIntent():
    # Check if request contains JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.json
    user_input = data.get("query", "")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    #question ="What is user asking for?"
    #prompt = f"Context: {user_input}\nQuestion: {question}"
    #prompt = f"what user is asking for by : {user_input} ?"
    # Craft the prompt to guide the model
    # Define examples in a separate variable
    examples_ = """
    User: I want to check dependencies for React 1.18.
    Assistant: Do you want to see the dependencies for React 1.18?

    User: Show vulnerabilities for React 1.18.
    Assistant: Do you want to see the vulnerabilities for React 1.18?

    User: Provide details about depandencies for XYZ 3.4.0.
    Assistant: Do you want to see the dependencies for XYZ 3.4.0?

    User: What are the vulnerabilities in abc?
    Assistant: Do you want to see the vulnerabilities for abc?
    """
    #TODO: add more prompts such that gpt-2 can be trained better
    examples = """
    User: I want to check dependency for React 1.18.
    Assistant: dependencies

    User: Show vulnrabilities for React 1.18.
    Assistant: vulnerabilities

    User: Provide details about dependencies for XYZ 3.4.0.
    Assistant: dependencies

    User: What are the vulnerbilities in abc?
    Assistant: vulnerabilities

    User: check vulnerbility in abc?
    Assistant: vulnerabilities

    User: check vulnerability in software 1.2?
    Assistant: vulnerabilities
    """
    prompt_template = f"{examples}\nUser: {{user_input}}\nAssistant:"

    # Craft the prompt using the examples variable
    # Prepare the prompt
    prompt = prompt_template.format(user_input=user_input)
 
    # Generate the response with a token limit
    max_tokens = 20  # Set the maximum number of tokens for the output
    temperature = 0.6  # Adjust temperature for randomness
    top_k = 50  # Limit to the top-k tokens
    try:
        response = llm.invoke(prompt,max_length=max_tokens, temperature= temperature, stop=["User:", "Assistant:"],).strip()
        #user_intent = llm.invoke(prompt)
        #response = llm.generate([prompt])  # Explicitly calling generate()

        user_intent = response.strip()  # Assuming response is a string
        # Extract framework and version
        framework, version = extractSoftware(user_input)


        # Modify the user intent based on extracted information
        if framework and version:
            user_intent = f"Do you want to see the {user_intent} for {framework} {version}?"
    except Exception as e:
        return jsonify({"error": f"LLM processing failed: {str(e)}"}), 500
     # Return the detected intent

    return jsonify({"intent": user_intent})

#the following two methods should be used with chatgpt 3 or higher version
def extractSoftware2(user_input):
    # Crafting the prompt to guide the model
    prompt = f"""
    Extract the software name and version from the following input:
    '{user_input}'

    Examples:
    Input: "Show vulnerabilities for Reakt 1.12"
    Output: Software: React, Version: 1.12

    Input: "Dependencies for Angular 12"
    Output: Software: Angular, Version: 12

    Input: "Provide details about Vue.js 2.6.0"
    Output: Software: Vue.js, Version: 2.6.0

    Now, extract the software and version for this input:
    '{user_input}'
    """
    
    # Sending the prompt to the LLM
    response = llm.invoke(prompt)
    print("line113: ",response)
    # Parsing the response to extract framework and version
    framework, version = parse_response(response)  # Define parse_response to handle the output format
    return framework, version

def parse_response(response):
    # Example parsing logic for the LLM output
    try:
        lines = response.splitlines()
        framework = None
        version = None
        for line in lines:
            if line.startswith("Software:"):
                framework = line.split(":")[1].strip()
            if line.startswith("Version:"):
                version = line.split(":")[1].strip()
        return framework, version
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None, None

#this is an alternative with limited capabilities of gpt-2. it should be replaced with the extractSoftware2 if using gpt3 or higher
#to get more accurate results including typo corrections
def extractSoftware(user_input):
    doc = nlp(user_input)
    framework = None
    version = None
    for ent in doc.ents:
        #if ent.label_ == "ORG":  # Could be 'React'
           # framework = ent.text
        if ent.label_ ==  "CARDINAL" or ent.label_ =="DATE":  # Could be '1.18'
            version = ent.text
    #extract software name. it should precede version      
    if version:
        version_position = user_input.find(version)
        text_before_version = user_input[:version_position].strip()
        framework = text_before_version.split()[-1]  # Get the last word before the version
        print("line165: ",framework, version)
        framework =getTypoCorrected(framework)
        print("line 167:", framework)
    # Generate the clarifying question
    if framework and version:
        question = f"Do you want to see the dependencies for {framework} {version}?"
        print(question)
        # return tuple with framework and version
        return framework,version
    else:
        return None, None

def getTypoCorrected(softwarename):
    # Step 1: Use PySpellChecker for basic typo correction
    spell = SpellChecker()
    corrected_name = spell.correction(softwarename)
    return corrected_name

#this is for higher gpt-3 or higher versions. Does not work for gpt-2
def getTypoCorrected2(softwarename):
    #ask LLM to correct the software name and return corrected software name
    prompt = f"Correct the typo in the following software name: '{softwarename}'Only return the corrected name."
    
    try:
        # Invoke the LLM (you might use a GPT-2, GPT-3, or any other model for this)
        corrected_name = llm.invoke(prompt).strip()
        print("line185: ",corrected_name)
        # Return the corrected software name
        return corrected_name
    except Exception as e:
        print(f"Error during typo correction: {e}")
        return softwarename  


# Function to generate SPARQL query from user input. Not only to be used with higher model. WIll not work for gpt-2
@app.route('/process_query', methods=['POST'])
def process_userinput():
    # Check if request contains JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.json
    user_input = data.get("query", "")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    #sparql_q = generate_sparqlhigherModel(user_input)  #this is to be used for advanced models --gpt-3 or higher. works great for gpt-4    
    query_results = generate_spqrql(user_input)   
    return jsonify({"sparqlresults":query_results})


def generate_spqrql(verified_intent):
    #extract software_name and software_intent
    match = re.search(r"dependencies for (\w+)\s+([\d.]+)|vulnerabilities for (\w+)\s+([\d.]+)", verified_intent, re.IGNORECASE)
    if match:
        software_name = match.group(1) or match.group(3)
        software_version = match.group(2) or match.group(4)
    else:
        return {"error": "Unable to extract software name or version from input."}

    # Step 2: Determine whether to generate query for dependencies or vulnerabilities
    if "dependencies" in verified_intent.lower():
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
    

    #-if verified_intent contains "vulnerabilities" then generate sparqle to get all vulnerabilities for a specified software and version
    elif "vulnerabilities" in verified_intent.lower():
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
    else:
        return {"error": "Unrecognized intent. Please specify 'dependencies' or 'vulnerabilities'."}
    print(query)
    results = graph.query(query)
    print(results)

    # Format results as a dictionary with software name and version as key and dictionary as a value 
    formatted_results = {f"{software_name} {software_version}": {}}
    for row in results:
        print("line 266:",row)
        for key, value in row.asdict().items():
            if key not in formatted_results[f"{software_name} {software_version}"]:
                formatted_results[f"{software_name} {software_version}"][key] = []
            formatted_results[f"{software_name} {software_version}"][key].append(value.toPython())

    return formatted_results


def generate_sparqlhigherModel(verified_intent):
    #provide accurate and detailed ontology description-classes, dependencies, URIs/IRIs
    ontology_description ="""
    Ontology includes the following:
    - Classes: Software, Software version, Hardware, Hardware version,Vulnerability,
    - Properties: dependsOn (URI: https://w3id.org/secure-chain/dependsOn), 
                  VulnerabeTo (URI: https://w3id.org/secure-chain/vulnerableTo)
    - Example: SoftwareA dependsOn SoftwareB, Software 1.10 VulnerableTo Vulnerability1
    """ 
     
    # Process verified_intent to make it suitable for SPARQL generation
    intent = verified_intent.replace("Do you want to see", "Get").strip()

     # Construct the LLM prompt
    prompt = (
        f"Using the following ontology description:\n{ontology_description}\n\n"
        f"Convert the following user input into a SPARQL query:\n'{intent}'"
    )

    sparql_query = llm.invoke(prompt).strip()

    # Validate and return the SPARQL query
    if not sparql_query:
        return jsonify({"error": "Failed to generate SPARQL query"}), 500

    return sparql_query 



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
    app.run(debug=True)
