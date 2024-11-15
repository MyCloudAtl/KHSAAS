import React, { useState, useEffect } from "react";
// import axios from 'axios';


//example sheet, need to perfect fetches and how datd is displayed look at return for what SBOM will return....should we add anything else?

const SBOM = () => {
    const [softwares, setSoftwares] = useState([]);
    const [softwareVersions, setSoftwareVersions] = useState([]);
    const [selectedSoftware, setSelectedSoftware] = useState('');
    const [selectedVersion, setSelectedVersion] = useState('');
    const [sbomData, setSbomData] = useState(null)
    // const navigate = useNavigate();

  useEffect(() => {
    const fetchSoftwares = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/softwares');
        setSoftwares(response.data);
      } catch (error) {
        console.error('Error generating softwares:', error);
      }
    };
    fetchSoftwares();
  }, []);

  useEffect(() => {
    if (selectedSoftware) {
      const fetchSoftwareVersions = async () => {
        try {
          const response = await axios.get(`http://localhost:5000/api/softwares/${selectedSoftware}/versions`);
          setSoftwareVersions(response.data);
        } catch (error) {
          console.error('Error generating software versions:', error);
        }
      };
      fetchSoftwareVersions();
    }
  }, [selectedSoftware]);

  useEffect(() => {
    if (selectedSoftware && selectedVersion) {
      const fetchSbomData = async () => {
        try {
          const response = await axios.get(`http://localhost:5000/api/sbom/${selectedSoftware}/${selectedVersion}`);
          setSbomData(response.data);
        } catch (error) {
          console.error('Error generating SBOM data:', error);
        }
      };
      fetchSbomData();
    }
  }, [selectedSoftware, selectedVersion]);


  const handleSoftwareChange = (e) => {
    setSelectedSoftware(e.target.value);
    setSelectedVersion('');
    setSbomData(null); // Reset 
  };

  const handleVersionChange = (e) => {
    setSelectedVersion(e.target.value);
  };

  const handleBackClick = () => {
    navigate('/');
  };

  return (
    <div className="sbom-container">
      <h2>SBOM Details</h2>
      <button onClick={handleBackClick}>Back to Home Page</button>

      <div className="selection-container">
        <div className="form-group">
          <label htmlFor="softwareName">Select Software</label>
          <select
            id="softwareName"
            name="softwareName"
            value={selectedSoftware}
            onChange={handleSoftwareChange}
            required
          >
            <option value="">Select Software</option>
            {softwares.map((software) => (
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
              name="softwareVersion"
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
          //manufacturer: Links Hardware to its Manufacturer.
          <p><strong>Hardware Version:</strong> {sbomData.hardwareVersion}</p>
          <p><strong>Depends on:</strong> {sbomData.softwareVersion}</p>
          <p><strong>Operates on:</strong> {sbomData.hardwareVersion}</p>
          <p><strong>License:</strong> {sbomData.license}</p>
          <p><strong>Organization Name:</strong> {sbomData.organizationName}</p> //discovered vulnerability
          <p><strong>Person Name:</strong> {sbomData.personName}</p> //discovered by
          //affiliation: relationship between Person & Organization.
          <p><strong>Vulnerability Type:</strong> {sbomData.vulnerabilityType}</p>
          <p><strong>Details:</strong> {sbomData.intangible}</p> //research paper - record of discovery
          <p><strong>Description:</strong> {sbomData.description}</p>
        </div>
      )}
    </div>
  );
};

export default SBOM;
