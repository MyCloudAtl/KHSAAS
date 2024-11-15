import React from 'react';
import { Link } from 'react-router-dom'

const Home = () =>{
    return(
        <div className='Landing-Page'>
            <h1>SAAS Supply Chain</h1>
            <section>
        <Link to='/ChatBot'>
            <button>Chat-Bot</button>
        </Link>
            </section>
            <section>
        <Link to='/SBOM'>
            <button>SBOM Search</button>
        </Link>
            </section>
            <section>
        <Link to='/Report'>
            <button>Report Risk</button>
        </Link>
            </section>
        </div>
    )
}
export default Home;