const axios = require('axios');

const endpoint = 'http://localhost:3030/kg';

exports.query = async (sparqlQuery) => {

    const response = await axios.post(endpoint, `query=${encodeURIComponent(sparqlQuery)}`, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
};