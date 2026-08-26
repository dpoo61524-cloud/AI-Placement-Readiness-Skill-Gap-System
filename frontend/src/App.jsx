import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from "react-router-dom";
import Upload from "./pages/Upload.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Recommendations from "./pages/Recommendations.jsx";
import api from "./api/client.js";

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [backendHealthy, setBackendHealthy] = useState(null);

  useEffect(() => {
    api.checkHealth()
      .then(() => setBackendHealthy(true))
      .catch(() => setBackendHealthy(false));
  }, []);

  const hasResult = !!analysisResult;

  return (
    <Router>
      <div className="app-container">

        {/* Aurora animated background */}
        <div className="aurora-bg" aria-hidden="true">
          <div className="aurora-blob b1" />
          <div className="aurora-blob b2" />
          <div className="aurora-blob b3" />
        </div>

        {/* Navbar */}
        <header className="navbar" style={{ justifyContent: "center" }}>
          <nav className="nav-links">
            <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
              Upload
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""} ${!hasResult ? "disabled-link" : ""}`}
              onClick={(e) => { if (!hasResult) e.preventDefault(); }}
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/recommendations"
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""} ${!hasResult ? "disabled-link" : ""}`}
              onClick={(e) => { if (!hasResult) e.preventDefault(); }}
            >
              Learning Path
            </NavLink>
          </nav>
        </header>

        {/* Content */}
        <main className="main-content">
          {backendHealthy === false && (
            <div className="error-banner">
              <strong>⚠ Backend Unreachable</strong> — Cannot connect to <code>http://localhost:8000</code>.
              Run: <code>python -m uvicorn backend.main:app --reload</code>
            </div>
          )}

          <Routes>
            <Route path="/" element={<Upload setAnalysisResult={setAnalysisResult} />} />
            <Route path="/dashboard" element={hasResult ? <Dashboard analysisResult={analysisResult} /> : <Navigate to="/" replace />} />
            <Route path="/recommendations" element={hasResult ? <Recommendations analysisResult={analysisResult} /> : <Navigate to="/" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
