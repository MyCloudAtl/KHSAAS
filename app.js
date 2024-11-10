const express = require('express');
const bodyParser = require('body-parser');
const sbomRoutes = require('./routes/sbomRoutes');

const app = express();
app.use(bodyParser.json());

app.use('/api', sbomRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

module.exports = app;