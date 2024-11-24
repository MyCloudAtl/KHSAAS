#TODOS:
#1. modify version extraction to account for different format in method extractSoftware
#2. Test functions with LLM_type= higher with LLAMA, gpt-3 or higher and Tune up as needed. 

#HIGHER LEVEL NOTES:gpt-4 can successfully convert user input to sparql query for even advanced query types. This was verified using chatgpt-4.0

from flask import Flask, request, jsonify
#from flask_cors import CORS  # Import CORS
#from rdflib import Graph
#from langchain_community.llms import OpenAI
from langchain_huggingface import HuggingFaceEndpoint
import json
import os
import spacy
from spellchecker import SpellChecker
import re
from rdflib.namespace import Namespace, RDF

#app = Flask(__name__)
#CORS(app)

# Read environment variables from .env file
#base_url = os.getenv('BASE_URL', 'http://localhost:3030')

# Existing SPARQL client setup
#SPARQL_ENDPOINT_URL = base_url + '/kg/'
#SPARQL_UPDATE_ENDPOINT_URL = base_url + '/kg/update'
#print(f"SPARQL endpoint is {SPARQL_ENDPOINT_URL}")

#sparql_client = SPARQLClient(SPARQL_ENDPOINT_URL, SPARQL_UPDATE_ENDPOINT_URL)

# Load the Turtle file
#graph = Graph()
#graph.parse("securechain.ttl", format="turtle")
#SC = Namespace("https://w3id.org/secure-chain/")
#SCHEMA = Namespace("http://schema.org/")
#graph.bind("sc", SC)
#graph.bind("schema", SCHEMA)


#NOTE: Switch LLM_type to lower for models lower than gpt-3.
#LLM_type = "higher"
LLM_type = "lower"

#NOTE: provide your api_key is using higher LLM_type. Change your model and import that (i.e import OpenAI)
api_key = ""
# Initialize the language model for generating SPARQL queries
#llm = OpenAI(model="gpt-3.5-turbo" , openai_api_key=api_key)

# Set your Hugging Face API token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
# Initialize the HuggingFace model
llm = HuggingFaceEndpoint(repo_id="gpt2", huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
nlp = spacy.load("en_core_web_sm")

#llm = Ollama(model="llama2")


def fetchIntent(user_input):
    print("I enter here in langchain for fetchIntent")
    #TODO: add more prompts such that gpt-2 can be trained better
    examples = """
    User: I want to check dependency for React 1.18.
    Assistant: dependencies

    User: Show vulnrabilities for React 1.18.
    Assistant: vulnerabilities

    User:  show vulnerabilities for python 3.
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
        user_intent = response.strip()  # Assuming response is a string
        # Extract framework and version
        framework, version = "default", "default"
        if LLM_type == "lower":
            framework, version = extractSoftware(user_input)       
            # Modify the user intent based on extracted information
            if framework and version:
                user_intent = f"Do you want to see the {user_intent} for {framework} {version}?"
        else:
            user_intent = extractUserIntent(user_input)

    except Exception as e:
        return jsonify({"error": f"LLM processing failed: {str(e)}"}), 500
     # Return the detected intent
    user_intent = re.sub(r"(dependencies|vulnerabilities):", r"\1", user_intent)
    print("line108",user_intent)
    return jsonify({"intent": user_intent})

#the following two methods should be used with chatgpt 3 or higher version
#TODO:train the model on other query types and to correct typos and spell check
def extractUserIntent(user_input):
    # Crafting the prompt to guide the model
    prompt = f"""
    Extract the software name and version from the following input:
    '{user_input}'

    Examples:
    Input: "Show vulnerabilities for Reakt 1.12"
    Output: "Do you want to see the vulnerabilities for React 1.12?"

    Input: "Dependencies for Angular 12"
    Output: "Do you want to see the vulnerabilities for Angular 12?"

    Input: "Provide details about Vue.js 2.6.0"
    Output: Do you want to see information about Vue.js 2.6.0?

    Now, extract user intent and frame as a question and return Output for this Input:
    '{user_input}'. Correct any typos and mis-spells as required.
    """
    
    # Sending the prompt to the LLM
    response = llm.invoke(prompt).strip()
    return response


#this is an alternative with limited capabilities of gpt-2. 
def extractSoftware(user_input):
    # Replace specific words followed by a colon (e.g., dependencies:, vulnerabilities:) with their respective names without the colon
    user_input = re.sub(r"(dependencies|vulnerabilities):", r"\1", user_input)
    print("colon processed",user_input)
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
        #framework =getTypoCorrected(framework)

    if framework and version:
        # return tuple with framework and version
        return framework,version
    else:
        return None, None

def getTypoCorrected(softwarename):
    # Step 1: Use PySpellChecker for basic typo correction
    spell = SpellChecker()
    corrected_name = spell.correction(softwarename)
    return corrected_name


def process_userinput(user_input):  
    print("I enter process_userinput")
    sparql_result =""
    if LLM_type == "lower":
        query_para = get_sparql_para(user_input)   
    else:
        sparql_q = generate_sparqlhigherModel(user_input)
        query_result = exetcute_query(sparql_q)
    #query_results = exetcute_query(query_q)
        #return jsonify({"queryResults":query_results}) #when switched to this, modify ChatBot.js file
    return query_para

#TODO: Modify version extraction.once version extraction is modified, modify the hardcoded value from this function
def get_sparql_para(verified_intent):
    #extract software_name and software_intent
    print("I enter get_sparql_para")
    match = re.search(r"dependencies for (\w+)\s+([\d.]+)|vulnerabilities for (\w+)\s+([\d.]+)", verified_intent, re.IGNORECASE)
    if match:
        software_name = match.group(1) or match.group(3)
        software_version = match.group(2) or match.group(4)
    else:
        return {"error": "Unable to extract software name or version from input."}
    print("softwareName:", software_name, "Version:",software_version)
    # Step 2: Determine whether to generate query for dependencies or vulnerabilities
    if "dependencies" in verified_intent.lower(): 
        querypara_result ={"type":"dependencies", "SoftwareName":software_name, "Version":software_version}     
        return querypara_result
    #-if verified_intent contains "vulnerabilities" then generate sparqle to get all vulnerabilities for a specified software and version
    elif "vulnerabilities" in verified_intent.lower():
        querypara_result ={"type":"vulnerability", "SoftwareName":software_name, "Version":software_version}     
        return querypara_result
    else:
        return {"error": "Unrecognized intent. Please specify 'dependencies' or 'vulnerabilities'."}


#TODO: provide examples for query formate such that it can be read
#TODO: provide detailed ontology description
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


#For Higher LLM. TODO Process query results 
def exetcute_query(query_spark):    
    #results = graph.query(query_spark)
    #result = sparql_client.query(query_spark)  
    result = sbom_service.execute_query(query_spark)
    return result#


#if __name__ == '__main__':
    #app.run(debug=True)