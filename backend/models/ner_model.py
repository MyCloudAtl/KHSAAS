import spacy

# Cargar el modelo de NER de spaCy
nlp = spacy.load("en_core_web_sm")

def identify_entities(sbom):
    sbom_text = str(sbom)
    doc = nlp(sbom_text)
    entities = []

    # Extraer entidades de tipo Software
    for ent in doc.ents:
        if ent.label_ == "ORG":  # Suponiendo que las entidades de tipo Software se etiquetan como ORG
            entities.append({ "entity": "Software", "value": ent.text })

    # Extraer entidades de tipo Dependency
    for ent in doc.ents:
        if ent.label_ == "PRODUCT":  # Suponiendo que las entidades de tipo Dependency se etiquetan como PRODUCT
            entities.append({ "entity": "Dependency", "value": ent.text })

    # Extraer entidades de tipo Vulnerability
    for ent in doc.ents:
        if ent.label_ == "NORP":  # Suponiendo que las entidades de tipo Vulnerability se etiquetan como NORP
            entities.append({ "entity": "Vulnerability", "value": ent.text })

    # Extraer entidades de tipo Metadata
    for ent in doc.ents:
        if ent.label_ == "MISC":  # Suponiendo que las entidades de tipo Metadata se etiquetan como MISC
            entities.append({ "entity": "Metadata", "value": ent.text })

    return entities