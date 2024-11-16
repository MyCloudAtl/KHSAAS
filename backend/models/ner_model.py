import spacy

nlp = None

def load_model():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

def identify_entities(sbom):
    load_model()
    sbom_text = str(sbom)
    doc = nlp(sbom_text)
    entities = []
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities.append({"entity": "Software", "value": ent.text})
        elif ent.label_ == "PRODUCT":
            entities.append({"entity": "Dependency", "value": ent.text})
        elif ent.label_ == "NORP":
            entities.append({"entity": "Vulnerability", "value": ent.text})
        elif ent.label_ == "MISC":
            entities.append({"entity": "Metadata", "value": ent.text})
    return entities
