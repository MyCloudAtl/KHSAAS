const express = require('express');
const router = express.Router();
const sbomController = require('../controllers/sbomController');

router.get('/sbom', sbomController.getSBOM);
module.exports = router;