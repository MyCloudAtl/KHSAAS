import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from 'axios';

const SBOM = () => {
    const [products, setProducts] = useState([]);
    const [versions, setVersions] = useState([]);
    const [selectedProducts, setSelectedProducts] = useState('');
    const [selectedVersion, setSelectedVersion] = useState('');
    const [sbomData, setSbomData] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [showSoftwareList, setShowSoftwareList] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [productName, setProductName] = useState('');
    const [suggestedProducts, setSuggestedProducts] = useState([]);

    // // Fetch software data on component mount
    // useEffect(() => {
    //     const fetchProducts = async () => {
    //         try {
    //             const response = await axios.get('http://localhost:5000/api/softwares');
    //             const products = Object.keys(response.data).map((key) => ({
    //                 name: key,
    //                 versions: response.data[key],
    //             }));
    //             setProducts(products);
    //         } catch (error) {
    //             console.error('Error fetching software list:', error);
    //         }
    //     };
    //     fetchProducts();
    // }, []);
    

    // // Fetch software versions when a software is selected
    // useEffect(() => {
    //     if (selectedProducts) {
    //         const fetchSoftwareVersions = async () => {
    //             try {
    //                 const response = await axios.get(`http://localhost:5000/api/softwares/${selectedProducts}/versions`);
    //                 console.log('Fetched versions:', response.data);
    //                 setVersions(response.data);
    //             } catch (error) {
    //                 console.error('Error fetching software versions:', error);
    //             }
    //         };
    //         fetchSoftwareVersions();
    //     }
    // }, [selectedProducts]);


    // useEffect(() => {
    //     if (selectedProducts && selectedVersion) {
    //         const fetch = async () => {
    //             try {
    //                 const response = await axios.get(`http://localhost:5000/api/sbom/${selectedProducts}/${selectedVersion}`);
    //                 console.log('Fetched SBOM data:', response.data);
    //                 const sbomItem = response.data[0];
    //             setSbomData({
    //                 ...sbomItem, 
    //             });
    //             } catch (error) {
    //                 console.error('Error fetching SBOM data:', error);
    //             }
    //         };
    //         fetchSbomData();
    //     }
    // }, [selectedProducts, selectedVersion]);

    // // Update software search query from URL on mount
    // useEffect(() => {
    //     const searchParams = new URLSearchParams(location.search);
    //     const searchQueryFromUrl = searchParams.get('search') || '';
    //     setSearchQuery(searchQueryFromUrl);
    // }, [location.search]);

    // // Update search query in the URL when the user types
    // const handleSearchChange = (e) => {
    //     const query = e.target.value;
    //     setSearchQuery(query);
    //     setShowSoftwareList(query.length > 0); 
    //     navigate(`?search=${query}`);
    // };
    
    // const handleSoftwareChange = (softwareName) => {
    //     setSelectedProducts(softwareName); 
    //     setSelectedVersion(''); 
    //     setSbomData(null);
    // };
    

    // const handleVersionChange = (e) => {
    //     setSelectedVersion(e.target.value);
    // };

    const handleBackClick = () => {
        navigate('/');
    };

    // const filteredproducts = products.filter((software) =>
    //     software.name.toLowerCase().includes(searchQuery.toLowerCase())
    // );    

    const handleProductNameChange = (e) => {
        setProductName(e.target.value);
    };

    // Handle form submission to fetch SBOM data
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!productName) return;
        const lowercasedProduct = productName.toLowerCase(); 
        setLoading(true);
        setError('');
        try {
            const response = await axios.get(`http://localhost:5000/api/sbom/${lowercasedProduct}`);
            console.log(response);
            const sbomItem = response.data[0];
            setSbomData({
                ...sbomItem, 
            }); 
            setSuggestedProducts([]);
            if (response.data.error) {
                throw new Error(response.data.error);
            }
    
        } catch (err) {
            setError('Failed to fetch SBOM data.');
            suggestSimilarProducts(lowercasedProduct);
        } finally {
            setLoading(false);
        }
    };

    // Suggest similar products based on the product name entered
    const suggestSimilarProducts = (productName) => {
        const similarityThreshold = 0.7; // Adjust threshold for similarity
        const fuzzyMatch = (str1, str2) => {
            const levenshtein = require('fast-levenshtein');
            const distance = levenshtein.get(str1, str2);
            const maxLength = Math.max(str1.length, str2.length);
            return (1 - distance / maxLength) >= similarityThreshold;
        };

        const suggestions = products.filter(product => 
            fuzzyMatch(product.name.toLowerCase(), productName)
        );
        
        setSuggestedProducts(suggestions);
    };
    

    return (
        <div className="sbom-container">
            <button onClick={handleBackClick}>Return Home</button>
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
                    <p><strong>Software Version:</strong> {decodeURIComponent(sbomData.softwareVersion)}</p>
                    <p><strong>Dependency On:</strong> {sbomData.dependency || 'No dependencies available'}</p>
                    <p><strong>Vulnerability:</strong> {sbomData.vulnerability}</p>
                </div>
            )}
        </div>
    );
};

export default SBOM;



