const sparqlClient = require('../utils/sparqlClient');
const nerService = require('./nerService');
const relationExtractionService = require('./relationExtractionService');

const dependenciesQuery = (softwareName, softwareVersion) => `
PREFIX sc: <https://w3id.org/secure-chain/>
PREFIX schema: <http://schema.org/>

SELECT ?softwareVersion ?dependency 

WHERE {
    ?software a sc:Software .
    ?software schema:name "${softwareName}" .
    ?software sc:hasSoftwareVersion ?softwareVersion .
    ?softwareVersion sc:versionName ?versionName .
    ?softwareVersion a sc:SoftwareVersion .
    ?softwareVersion sc:versionName "${softwareVersion}" .
    ?softwareVersion sc:dependsOn ?dependency .
}
`;

const vulnerabilitiesQuery = (softwareName, softwareVersion) => `
    PREFIX sc: <https://w3id.org/secure-chain/>
    PREFIX schema: <http://schema.org/>
    SELECT ?softwareVersion ?vulnerability WHERE {
        ?software a sc:Software .
        ?software schema:name "${softwareName}" .
        ?software sc:hasSoftwareVersion ?softwareVersion .
        ?softwareVersion sc:versionName "${softwareVersion}" .
        ?softwareVersion sc:vulnerableTo ?vulnerability .
    }
`;

exports.generateSBOM = async (softwareName, softwareVersion) => {

    // SBOM object
    const sbom = {
        software: softwareName,
        version: softwareVersion,
        dependencies: [],
        vulnerabilities: [],
    };

    // GET dependencies
    const dependenciesResponse = await sparqlClient.query(dependenciesQuery(softwareName, softwareVersion));
    sbom.dependencies = dependenciesResponse.results.bindings.map(binding => binding.dependency.value);

    // // GET vulnerabilities
    // const vulnerabilitiesResponse = await sparqlClient.query(vulnerabilitiesQuery(softwareName, softwareVersion));
    // sbom.vulnerabilities = vulnerabilitiesResponse.results.bindings.map(binding => binding.vulnerability.value);


    // // Identify entities from sbom
    // const nerResults = await nerService.identifyEntities(sbom);

    // // Extract relations from entities
    // const relationResults = await relationExtractionService.extractRelations(nerResults);
    // sbom.enrichedData = relationResults;

    return sbom;
};