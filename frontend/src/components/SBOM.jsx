import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from 'axios';

const SBOM = () => {
    const [softwares, setSoftwares] = useState([]);
    const [softwareVersions, setSoftwareVersions] = useState([]);
    const [selectedSoftware, setSelectedSoftware] = useState('');
    const [selectedVersion, setSelectedVersion] = useState('');
    const [sbomData, setSbomData] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showSoftwareList, setShowSoftwareList] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    // Fetch software data on component mount
    useEffect(() => {
        const fetchSoftwares = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/softwares');
                const softwares = Object.keys(response.data).map((key) => ({
                    name: key,
                    versions: response.data[key],
                }));
                setSoftwares(softwares);
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
                    console.log('Fetched versions:', response.data);
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
        setShowSoftwareList(query.length > 0); // Show the software list when typing
        navigate(`?search=${query}`);
    };

    // const handleSoftwareChange = (softwareName) => {
    //     setSelectedSoftware(softwareName);
    //     setSelectedVersion('');
    //     setSbomData(null); 
    //     setShowSoftwareList(false); 
    // };

    
    const handleSoftwareChange = (softwareName) => {
        setSelectedSoftware(softwareName); // Update selected software
        setSelectedVersion(''); // Reset version
        setSbomData(null); // Reset SBOM data
    };
    

    const handleVersionChange = (e) => {
        setSelectedVersion(e.target.value);
    };

    const handleBackClick = () => {
        navigate('/');
    };

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
                    onFocus={() => setShowSoftwareList(true)} 
                    onBlur={() => setTimeout(() => setShowSoftwareList(false), 200)} 
                />
                {/* Software List Dropdown */}
                {showSoftwareList && searchQuery && (
                    <ul className="software-list-dropdown">
                    {filteredSoftwares.length > 0 ? (
                        filteredSoftwares.map((software, index) => (
                            <li
                                key={software.name + index}  // Ensures a unique key
                                onClick={() => handleSoftwareChange(software.name)} 
                            >
                                {software.name}
                            </li>
                        ))
                    ) : (
                        <li>No matching software found</li>
                    )}
                </ul>
                )}
            </div>

            <div className="selection-container">
                <div className="form-group">
                    <label htmlFor="softwareName">Select Software</label>
                    <select
                        id="softwareName"
                        value={selectedSoftware}
                        onChange={(e) => handleSoftwareChange(e.target.value)}
                        required
                    >
                        <option value="">Select Software</option>
                        {filteredSoftwares.map((software, index) => (
                            <option key={software.name + index} value={software.name}>
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
                                <option key={version} value={version}>
                                    {version}
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



