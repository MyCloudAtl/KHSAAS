from models.relation_extraction_model import extract_relations as re_extract_relations

def extract_relations(ner_results):
    relation_results = re_extract_relations(ner_results)
    return relation_results