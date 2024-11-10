const sparqlClient = require('../utils/sparqlClient');
const nerService = require('./nerService');
const relationExtractionService = require('./relationExtractionService');

exports.generateSBOM = async (software) => {

    // SBOM object
    const sbom = {
        software: software,
        dependencies: [],
        vulnerabilities: [],
        metadata: {}
    };

    // GET dependencies
    const dependenciesQuery = `
        SELECT ?dependency 
        WHERE {
            <${software}> <http://example.org/dependsOn> ?dependency .
        }`;
    const dependenciesResponse = await sparqlClient.query(dependenciesQuery);
    sbom.dependencies = dependenciesResponse.results.bindings.map(binding => binding.dependency.value);

    // GET vulnerabilities
    const vulnerabilitiesQuery = `
        SELECT ?vulnerability 
        WHERE {
            <${software}> <http://example.org/hasVulnerability> ?vulnerability .
        }`;
    const vulnerabilitiesResponse = await sparqlClient.query(vulnerabilitiesQuery);
    sbom.vulnerabilities = vulnerabilitiesResponse.results.bindings.map(binding => binding.vulnerability.value);

    // GET metadata 
    const metadataQuery = `
        SELECT ?p ?o 
        WHERE {
            <${software}> ?p ?o .
        }`;
    const metadataResponse = await sparqlClient.query(metadataQuery);
    metadataResponse.results.bindings.forEach(binding => {
        sbom.metadata[binding.p.value] = binding.o.value;
    });

    // Identify entities from sbom
    const nerResults = await nerService.identifyEntities(sbom);

    // Extract relations from entities
    const relationResults = await relationExtractionService.extractRelations(nerResults);
    sbom.enrichedData = relationResults;

    return sbom;
};