import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
// import axios from 'axios';

const SBOM = () => {
    const [softwares, setSoftwares] = useState([]);
    const [softwareVersions, setSoftwareVersions] = useState([]);
    const [selectedSoftware, setSelectedSoftware] = useState('');
    const [selectedVersion, setSelectedVersion] = useState('');
    const [sbomData, setSbomData] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    // Fetch software data on component mount
    useEffect(() => {
        const fetchSoftwares = async () => {
            try {
                const response = await axios.get('http://localhost:5000/softwares');
                setSoftwares(response.data);
            } catch (error) {
                console.error('Error fetching software list:', error);
            }
        };
        fetchSoftwares();
    }, []);

    // Fetch software versions when a software is selected
    useEffect(() => {
        if (selectedSoftware) {
            const fetchSoftwareVersions = async () => {
                try {
                    const response = await axios.get(`http://localhost:5000/api/softwares/${selectedSoftware}/versions`);
                    setSoftwareVersions(response.data);
                } catch (error) {
                    console.error('Error fetching software versions:', error);
                }
            };
            fetchSoftwareVersions();
        }
    }, [selectedSoftware]);

    // Fetch SBOM data when a software and version are selected
    useEffect(() => {
        if (selectedSoftware && selectedVersion) {
            const fetchSbomData = async () => {
                try {
                    const response = await axios.get(`http://localhost:5000/api/sbom/${selectedSoftware}/${selectedVersion}`);
                    setSbomData(response.data);
                } catch (error) {
                    console.error('Error fetching SBOM data:', error);
                }
            };
            fetchSbomData();
        }
    }, [selectedSoftware, selectedVersion]);

    // Update software search query from URL on mount
    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);
        const searchQueryFromUrl = searchParams.get('search') || '';
        setSearchQuery(searchQueryFromUrl);
    }, [location.search]);

    // Update search query in the URL when the user types
    const handleSearchChange = (e) => {
        const query = e.target.value;
        setSearchQuery(query);
        navigate(`?search=${query}`);
    };

    const handleSoftwareChange = (e) => {
        setSelectedSoftware(e.target.value);
        setSelectedVersion('');
        setSbomData(null); // Reset SBOM data
    };

    const handleVersionChange = (e) => {
        setSelectedVersion(e.target.value);
    };

    const handleBackClick = () => {
        navigate('/');
    };

    // Filter software list based on search query
    const filteredSoftwares = softwares.filter((software) =>
        software.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="sbom-container">
            <button onClick={handleBackClick}>Return Home</button>
            <h2>SBOM Details</h2>

            {/* Search Input */}
            <div className="search-container">
                <label htmlFor="softwareSearch">Search Software</label>
                <input
                    type="text"
                    id="softwareSearch"
                    value={searchQuery}
                    onChange={handleSearchChange}
                    placeholder="Search software..."
                />
            </div>

            <div className="selection-container">
                <div className="form-group">
                    <label htmlFor="softwareName">Select Software</label>
                    <select
                        id="softwareName"
                        value={selectedSoftware}
                        onChange={handleSoftwareChange}
                        required
                    >
                        <option value="">Select Software</option>
                        {filteredSoftwares.map((software) => (
                            <option key={software.id} value={software.id}>
                                {software.name}
                            </option>
                        ))}
                    </select>
                </div>

                {selectedSoftware && (
                    <div className="form-group">
                        <label htmlFor="softwareVersion">Select Version</label>
                        <select
                            id="softwareVersion"
                            value={selectedVersion}
                            onChange={handleVersionChange}
                            required
                        >
                            <option value="">Select Version</option>
                            {softwareVersions.map((version) => (
                                <option key={version.id} value={version.id}>
                                    {version.versionName}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            {sbomData && (
                <div className="sbom-data">
                    <h3>SBOM Data for {selectedSoftware} - {selectedVersion}</h3>
                    <p><strong>Vulnerability:</strong> {sbomData.vulnerability}</p>
                    <p><strong>Hardware:</strong> {sbomData.hardwareName}</p>
                    <p><strong>Hardware Version:</strong> {sbomData.hardwareVersion}</p>
                    <p><strong>Depends on:</strong> {sbomData.softwareVersion}</p>
                    <p><strong>Operates on:</strong> {sbomData.hardwareVersion}</p>
                    <p><strong>License:</strong> {sbomData.license}</p>
                    <p><strong>Organization Name:</strong> {sbomData.organizationName}</p>
                    <p><strong>Person Name:</strong> {sbomData.personName}</p>
                    <p><strong>Vulnerability Type:</strong> {sbomData.vulnerabilityType}</p>
                    <p><strong>Details:</strong> {sbomData.intangible}</p>
                    <p><strong>Description:</strong> {sbomData.description}</p>
                </div>
            )}
        </div>
    );
};

export default SBOM;

