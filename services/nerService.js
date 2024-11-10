const nerModel = require('../models/nerModel');

exports.identifyEntities = async (sbom) => {
    const nerResults = await nerModel.identifyEntities(sbom);
    return nerResults;
};