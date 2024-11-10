const sbomService = require('../services/sbomService');

exports.getSBOM = async (req, res) => {
    try {
        const software = req.query.software;
        const sbom = await sbomService.generateSBOM(software);
        res.json(sbom);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};