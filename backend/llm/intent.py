import requests
import os

BASE = "http://localhost:5055"

SOFTWARE_LIST= "/api/softwares"
SOFTWARE_VERSIONS = "/get_versions"
SOFTWARE_DEPENDENCIES="/api/dependencies" #Params: name, version
SOFTWARE_SBOM="/api/sbom" #POST: name, version
SOFTWARE_VULNERABILITES="/api/vulnerabilities"

# Setup lib
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
import google.generativeai as genai
from typing import Literal

from dotenv import load_dotenv
load_dotenv()

# Define User intent enum
class Classification(BaseModel):
    """
    A few-shot example of text classification:

    Examples:
    - "Get me the list of software!": SOFTWARE_LIST
    - "What are the versions for this software": SOFTWARE_VERSIONS
    - "What are libraries are used for aws-sdk": SOFTWARE_DEPENDENCIES
    - "List the vulnerabilities in linux?": SOFTWARE_VULNERABILITES
    - "Generate the SBOM for whisper": SOFTWARE_SBOM
    - "Write me a haiku": UNKNOWN
    """

    chain_of_thought: str = Field(
        ...,
        description="The chain of thought that led to the prediction.",
    )
    label: Literal["SOFTWARE_LIST", "SOFTWARE_VERSIONS", "SOFTWARE_DEPENDENCIES",
                    "SOFTWARE_VULNERABILITES", "SOFTWARE_SBOM", "UNKNOWN"] = Field(
        ...,
        description="The predicted class label.",
    )

# Define output
class SoftwareQuery(BaseModel):
    name: str
    version: str
    intent: Classification

ollama_setup = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
gemini_setup = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/", api_key=os.getenv("GOOGLE_API_KEY"))
client = instructor.from_openai(
    gemini_setup,
    mode=instructor.Mode.JSON,
)

def user_intent(query):
    return client.chat.completions.create(
        # model="llama3.2",
        model="gemini-1.5-flash",
        n=2,
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        response_model=SoftwareQuery,
    )

def handle_intent(query):
    response = user_intent(query)
    print(response)
    # print(f"Name:{res.name}\nVersion:{res.version}\nIntent:{res.intent.label}")
    name = response.name
    version = response.version

    # Get user intent classification
    match response.intent.label:
        case "SOFTWARE_LIST":
            response = requests.get(BASE + SOFTWARE_LIST)
            return response.json()
            
        case "SOFTWARE_VERSIONS":
            if not name:
                raise ValueError("Software name is required")
            response = requests.get(f"{BASE}{SOFTWARE_VERSIONS}?name={name}")
            return response.json()
            
        case "SOFTWARE_DEPENDENCIES":
            if not name or not version:
                raise ValueError("Software name and version are required")
            response = requests.get(f"{BASE}{SOFTWARE_DEPENDENCIES}?name={name}&version={version}")
            return response.json()
            
        case "SOFTWARE_VULNERABILITES":
            if not name or not version:
                raise ValueError("Software name and version are required")
            response = requests.get(f"{BASE}{SOFTWARE_VULNERABILITES}?name={name}&version={version}")
            return response.json()
            
        case "SOFTWARE_SBOM":
            if not name or not version:
                raise ValueError("Software name and version are required")
            response = requests.post(BASE + SOFTWARE_SBOM, json={
                "name": name,
                "version": version
            })
            return response.json()
            
        case _:
            raise ValueError(f"Unknown intent: {response.intent.chain_of_thought}")
