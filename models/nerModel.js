const nlp = require('compromise');

exports.identifyEntities = async (sbom) => {
    const sbomText = JSON.stringify(sbom);
    const doc = nlp(sbomText);
    const entities = [];



    doc.match('#Software').json().forEach(software => {
        entities.push({ entity: 'Software', value: software.text });
    });

    doc.match('#Dependency').json().forEach(dependency => {
        entities.push({ entity: 'Dependency', value: dependency.text });
    });

    doc.match('#Vulnerability').json().forEach(vulnerability => {
        entities.push({ entity: 'Vulnerability', value: vulnerability.text });
    });

    doc.match('#Metadata').json().forEach(metadata => {
        entities.push({ entity: 'Metadata', value: metadata.text });
    });

    return entities;
};