import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const SBOM = () => {
  const [sbomData, setSbomData] = useState([]);
  const [recData, setRecData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [productName, setProductName] = useState("");

    const navigate = useNavigate();

  const handleProductNameChange = (e) => setProductName(e.target.value);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!productName) return;

    setLoading(true);
    setError("");
    try {
      const response = await axios.get(
        `http://localhost:5000/api/sbom/${encodeURIComponent(productName)}`
      );

      if (response.data.error) throw new Error(response.data.error);

      setSbomData(response.data.sbomData);
      setRecData(response.data.recData);
    } catch (err) {
      setError("Failed to fetch SBOM data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sbom-container">
      <button className="home-button" onClick={() => navigate("/")}>
        Return Home
      </button>
      <h2>SBOM Details</h2>

      <form onSubmit={handleSubmit} className="product-form">
        <div className="form-group">
          <label htmlFor="productName">Product Name</label>
          <input
            type="text"
            id="productName"
            value={productName}
            onChange={handleProductNameChange}
            placeholder="Enter product name"
            required
            className="input-field"
          />
        </div>
        <button type="submit" className="submit-button" disabled={loading}>
          Get SBOM Data
        </button>
      </form>

      {loading && <p className="loading-text">Loading...</p>}
      {error && <div className="error-message">{error}</div>}

      {sbomData.length > 0 && (
        <div className="scrollable-data">
          <h3>SBOM Data for {productName}</h3>
          {sbomData.map((item, index) => (
            <div key={index} className="sbom-item">
              <p><strong>Software Version:</strong> {item.softwareVersion}</p>
              <p><strong>Dependency On:</strong> {item.dependency}</p>
              <p><strong>Vulnerability:</strong> {item.vulnerability}</p>
              <hr />
            </div>
          ))}
        </div>
      )}

      {recData.length > 0 && (
        <div className="scrollable-data">
          <h3>Safe {productName} Versions</h3>
          {recData.map((item, index) => (
            <div key={index} className="recommendation-item">
              <p><strong>Recommended Version:</strong> {item.softwareVersion}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SBOM;




