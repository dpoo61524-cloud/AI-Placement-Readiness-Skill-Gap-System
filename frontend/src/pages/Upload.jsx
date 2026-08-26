import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client.js";

function Upload({ setAnalysisResult }) {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
        setError(null);
      } else {
        setError("Only PDF resumes are supported.");
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a resume PDF file.");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Please provide a target Job Description.");
      return;
    }

    setLoading(true);
    setError(null);
    setLoadingStep("Uploading resume PDF...");

    const stepTimer1 = setTimeout(() => setLoadingStep("Parsing resume details and extracting profile info..."), 1500);
    const stepTimer2 = setTimeout(() => setLoadingStep("Evaluating placement readiness with ML model..."), 3500);
    const stepTimer3 = setTimeout(() => setLoadingStep("Computing feature contributions via SHAP..."), 5500);
    const stepTimer4 = setTimeout(() => setLoadingStep("Calculating semantic skill gaps & generating learning plan..."), 7500);

    try {
      const result = await api.runFullAnalysis(file, jobDescription);
      
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      clearTimeout(stepTimer4);
      
      setAnalysisResult(result);
      navigate("/dashboard");
    } catch (err) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      clearTimeout(stepTimer4);
      console.error(err);
      setError(
        err.response?.data?.detail || 
        "An error occurred while analyzing the files. Please ensure the backend is running."
      );
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
        <h1 className="page-title" style={{ fontSize: "2.6rem", marginBottom: "0.75rem" }}>
          AI Placement Readiness & Skill Gap System
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem", maxWidth: "650px", margin: "0 auto", lineHeight: 1.6 }}>
          Upload your resume PDF and paste the target job description below to calculate your placement readiness score, identify semantic skill gaps, and receive a personalized 4-week learning roadmap.
        </p>
      </div>

      <div className="card highlight" style={{ padding: "2.5rem" }}>
        {error && <div className="error-banner">{error}</div>}

        {loading ? (
          <div className="loading-screen">
            <div className="loading-ring"></div>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)" }}>
              Analyzing Application
            </h3>
            <p className="animate-pulse-soft" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
              {loadingStep}
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Step 1: Upload Resume (PDF)</label>
              
              <div 
                className={`upload-zone ${dragActive ? "drag-active" : ""} ${file ? "has-file" : ""}`}
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={triggerFileSelect}
              >
                <input 
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".pdf"
                  style={{ display: "none" }}
                />
                <div className="upload-icon">{file ? "✅" : "📄"}</div>
                {file ? (
                  <div>
                    <p style={{ fontWeight: 700, color: "var(--text-primary)" }}>{file.name}</p>
                    <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                      {(file.size / (1024 * 1024)).toFixed(2)} MB • Click/drop to replace
                    </p>
                  </div>
                ) : (
                  <div>
                    <p style={{ fontWeight: 700, color: "var(--text-primary)" }}>Drag and drop resume PDF here</p>
                    <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "4px" }}>or click to browse from files</p>
                  </div>
                )}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Step 2: Target Job Description</label>
              <textarea 
                className="form-input textarea"
                placeholder="Paste the target job description here... (e.g. Seeking a Full Stack Engineer with Python, React, and SQL database skills...)"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>

            <div style={{ marginTop: "2rem" }}>
              <button type="submit" className="btn btn-primary" style={{ width: "100%", padding: "1rem" }} disabled={!file || !jobDescription.trim()}>
                🚀 Analyze Placement Readiness
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default Upload;
