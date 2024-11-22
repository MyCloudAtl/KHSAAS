import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from 'axios';

const SBOM = () => {
    const [sbomData, setSbomData] = useState([]);
    const [recData, setRecData] = useState([]);
    const navigate = useNavigate();
    const location = useLocation();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [productName, setProductName] = useState('');
    const [suggestedProducts, setSuggestedProducts] = useState([]);

    const handleProductNameChange = (e) => {
        setProductName(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!productName) return;
        const encodedProduct = encodeURIComponent(productName.toLowerCase());  // URL-encode the product name
        setLoading(true);
        setError('');
        try {
            const response = await axios.get(`http://localhost:5000/api/sbom/${encodedProduct}`);
            console.log(response);
            const sbomItem = response.data.sbomData[0];
            setSbomData(sbomItem);
            const recItem = response.data.recData[0];
            setRecData(recItem);
            if (response.data.error) {
                throw new Error(response.data.error);
            }
        } catch (err) {
            setError('Failed to fetch SBOM data.');
        } finally {
            setLoading(false);
        }
    };    

    return (
        <div className="sbom-container">
            <button onClick={() => navigate('/')}>Return Home</button>
            <h2>SBOM Details</h2>

            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="productName">Product Name</label>
                    <input
                        type="text"
                        id="productName"
                        value={productName}
                        onChange={handleProductNameChange}
                        placeholder="Enter product name"
                        required
                    />
                </div>
                <button type="submit" disabled={loading}>Get SBOM Data</button>
            </form>

            {loading && <p>Loading...</p>}
            {error && <p>{error}</p>}

            {sbomData && (
                <div className="sbom-data">
                <h3>SBOM Data for {productName}</h3>
                    <p><strong>Software Version:</strong> {sbomData.softwareVersion}</p>
                    <p><strong>Dependency On:</strong> {sbomData.dependency || 'No dependencies available'}</p>
                    <p><strong>Vulnerability:</strong> {sbomData.vulnerability}</p>
                </div>
            )}
            {recData && (
                <div className="rec-data">
                <h3>Safe {productName} Versions: </h3>
                    <p><strong>Recommendation:</strong> {recData.softwareVersion}</p>
                </div>
            )}
        </div>
    );
};

export default SBOM;



