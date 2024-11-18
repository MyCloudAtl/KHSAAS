from models.ner_model import identify_entities as ner_identify_entities
from models.relation_extraction_model import extract_relations as re_extract_relations

class RelationExtractionService:
    def __init__(self):
        # Inicializar los modelos si es necesario
        pass

    def identify_entities(self, text):
        return ner_identify_entities(text)

    def extract_relations(self, ner_results):
        return re_extract_relations(ner_results)



# Just for test sake, not part of the actual code
if __name__ == "__main__":
    service = RelationExtractionService()
    text = "Your input text here"
    ner_results = service.identify_entities(text)
    relation_results = service.extract_relations(ner_results)
    print(relation_results)