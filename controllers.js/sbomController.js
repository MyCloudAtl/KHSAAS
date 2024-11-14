const sbomService = require('../services/sbomService');

exports.getSBOM = async (req, res) => {
    try {
        const software = req.query.software;
        const version = req.query.version;
        console.log("Antes de llamar a generateSBOM en controller");
        // Error calling sbomService.generateSBOM
        const sbom = await sbomService.generateSBOM(software, version);
        console.log("Antes de devovler el SBOm en controller");
        res.json(sbom);
    } catch (error) {
        console.log("Keubo  error por aqui en controller");
        res.status(500).json({ error: error.message });
    }
};