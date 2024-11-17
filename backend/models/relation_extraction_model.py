def extract_relations(ner_results):

    relations = []
    for entity in ner_results:
        if entity["entity"] == "Software":

            relations.append({'source': entity['value'], 'target': 'Dependency', 'relation': 'dependsOn'})
    return {'relations': relations}
