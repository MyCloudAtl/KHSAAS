from models.ner_model import identify_entities as ner_identify_entities

def identify_entities(sbom):
    ner_results = ner_identify_entities(sbom)
    return ner_results