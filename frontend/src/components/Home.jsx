import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
    const [darkMode, setDarkMode] = useState(false);

    const toggleTheme = () => {
        setDarkMode(!darkMode);
        document.body.classList.toggle('dark-theme', !darkMode);
    };

    return (
        <div className={`Landing-Page ${darkMode ? 'dark' : ''}`}>
            <header className="hero">
                <h1 className="animated-headline">SAAS Supply Chain</h1>
                <button className="theme-toggle" onClick={toggleTheme}>
                    {darkMode ? 'Light Mode' : 'Dark Mode'}
                </button>
            </header>

            <section className="section">
                <Link to='/ChatBot'>
                    <button className="home-button">Chat-Bot</button>
                </Link>
            </section>

            <section className="section">
                <Link to='/SBOM'>
                    <button className="home-button">SBOM Search</button>
                </Link>
            </section>

            {/* <section className="section">
                <Link to='/Report'>
                    <button className="home-button">Report Risk</button>
                </Link>
            </section> */}
        </div>
    );
};

export default Home;
