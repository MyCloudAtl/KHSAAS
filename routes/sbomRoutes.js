const express = require('express');
const router = express.Router();
const sbomController = require('../controllers.js/sbomController');

router.get('/sbom', sbomController.getSBOM);
module.exports = router;