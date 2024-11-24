import React, { useState } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import './App.css'
import Home from './components/Home'
import Report from './components/Report'
import SBOM from './components/SBOM'
import ChatBot from './components/ChatBot'

function App() {

  return (
    <div className="App-Container">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/Report" element={<Report />} />
        <Route path="/SBOM" element={<SBOM />} />
        <Route path="/ChatBot" element={<ChatBot />} />
      </Routes>
    </div>
  )
}

export default App
