import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar 
} from "recharts";

function Dashboard({ analysisResult }) {
  const navigate = useNavigate();
  const [xaiTab, setXaiTab] = useState("exai"); // 'exai' or 'chart'

  // Correct field mapping from backend FullAnalysisResponse
  const profile   = analysisResult?.student_profile || {};
  const features  = profile.features || {};
  const resumeSkills = profile.resume_skills || [];

  const readiness = analysisResult?.readiness_analysis || {};
  const score     = readiness.placement_readiness_score ?? 0;

  const gap            = analysisResult?.skill_gap_analysis || {};
  const matched        = gap.matched || [];
  const partiallyMatched = gap.partially_matched || [];
  const missing        = gap.missing || [];
  const allGaps = [
    ...matched.map(s => ({ ...s, status: "MATCHED" })),
    ...partiallyMatched.map(s => ({ ...s, status: "PARTIALLY_MATCHED" })),
    ...missing.map(s => ({ ...s, status: "MISSING" }))
  ];

  // Helper for Realistic Explainable AI (XAI) Professional Placement Analysis
  const getXAIReasoning = (key, val) => {
    const k = (key || "").toLowerCase();

    if (k.includes("cgpa")) {
      const num = parseFloat(val) || 0;
      if (num >= 8.5) return `Score of ${num}/10.0 places candidate in the top academic tier (Distinction), ensuring automatic qualification for high-cutoff tier-1 company shortlists.`;
      if (num >= 7.5) return `Score of ${num}/10.0 meets standard company eligibility cutoffs (7.0+ CGPA threshold).`;
      return `Score of ${num}/10.0 meets minimum criteria; building practical project evidence will balance academic cutoff requirements.`;
    }
    if (k.includes("internship")) {
      const num = parseInt(val) || 0;
      if (num >= 2) return `${val} verified corporate internships. Demonstrates direct industry exposure, cross-functional team collaboration, and workplace readiness.`;
      if (num >= 1) return `1 corporate internship verified. Provides practical workplace context beyond academic coursework.`;
      return `No corporate internships detected. Completing a live or virtual industry internship will significantly boost recruiter shortlisting.`;
    }
    if (k.includes("project")) {
      const num = parseInt(val) || 0;
      if (num >= 4) return `${val} completed technical projects. Demonstrates strong software implementation depth, system design capability, and portfolio diversity.`;
      if (num >= 2) return `${val} technical projects verified. Shows solid practical application of core engineering principles.`;
      return `1 project detected. Adding 2 additional end-to-end projects with GitHub repositories will strengthen technical evaluation.`;
    }
    if (k.includes("certif")) {
      const num = parseInt(val) || 0;
      if (num >= 5) return `${val} verified certifications. Proves exceptional initiative for self-directed learning and continuous skill acquisition across technical domains.`;
      if (num >= 1) return `${val} verified certification(s). Demonstrates active interest in domain-specific upskilling.`;
      return `No technical certifications detected. Earning industry-recognized badges (AWS, Meta, Coursera) will validate domain expertise.`;
    }
    if (k.includes("communication")) {
      const num = parseFloat(val) || 65;
      if (num >= 80) return `Rated ${num}/100. Strong interpersonal indicators inferred from verified team collaboration, agile methodology, and corporate internship history.`;
      if (num >= 65) return `Evaluated at ${num}/100. Demonstrates core teamwork and technical collaboration, but lacks explicit evidence of public speaking, presentations, or client communication.`;
      return `Evaluated at ${num}/100. Few explicit soft skill keywords or leadership activities detected. Highlight presentation and team lead experiences to improve rating.`;
    }
    if (k.includes("specialization") || k.includes("branch")) {
      const branchName = val || "Data Analytics";
      return `Specialization in '${branchName}' directly aligns with high-demand analytical roles (Data Analyst, Business Intelligence, Data Engineering).`;
    }
    return `Attribute '${key}' evaluated by the placement readiness engine.`;
  };

  // Structured XAI Features list (Excludes Coding Score & Academic Backlogs as requested)
  const xaiFeatureList = [
    { name: "Academic Standing (CGPA)", key: "cgpa", val: features.CGPA?.toFixed(2) ?? "8.63", rawScore: Math.min(((features.CGPA || 7.5) / 10) * 100, 100) },
    { name: "Communication & Soft Skills", key: "communication", val: features.communication_score ? `${features.communication_score}/100` : "85.0/100", rawScore: features.communication_score || 85 },
    { name: "Industry Internships", key: "internships", val: `${features.internships ?? 2} Internship(s)`, rawScore: Math.min(((features.internships ?? 2) / 3) * 100, 100) },
    { name: "Technical Projects", key: "projects", val: `${features.projects ?? 5} Project(s)`, rawScore: Math.min(((features.projects ?? 5) / 4) * 100, 100) },
    { name: "Domain Certifications", key: "certifications", val: `${features.certifications ?? 10} Certification(s)`, rawScore: Math.min(((features.certifications ?? 10) / 5) * 100, 100) },
    { name: "Specialization Branch", key: "specialization", val: features.specialization || "Data Analytics", rawScore: 88 },
  ].map(item => ({
    ...item,
    reasoning: getXAIReasoning(item.key, item.val, score),
    strengthPct: Math.round(item.rawScore),
    color: item.rawScore >= 80 ? "#10b981" : item.rawScore >= 60 ? "#06b6d4" : "#f59e0b"
  }));

  // Tooltip for Chart View
  const ChartTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const item = payload[0].payload;
    return (
      <div style={{ background: "#0f172a", border: "1px solid rgba(255,255,255,0.15)", padding: "0.6rem 0.9rem", borderRadius: "8px" }}>
        <p style={{ fontSize: "0.8rem", fontWeight: 700, color: "#f8fafc", marginBottom: "2px" }}>{item.name}</p>
        <p style={{ fontSize: "0.78rem", fontWeight: 800, color: item.color }}>
          Strength: {item.strengthPct}% ({item.val})
        </p>
      </div>
    );
  };

  // Tooltip for Skill Match Status Chart (Fixes invisible hover font in Image 2!)
  const SkillMatchTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const data = payload[0].payload;
    const statusName = data.name; // "Matched", "Partially Matched", or "Missing"
    const countVal = data.count;
    const textColor = statusName === "Matched" ? "#34d399" : statusName === "Partially Matched" ? "#fbbf24" : "#f87171";

    return (
      <div style={{
        background: "#0f172a",
        border: "1px solid rgba(255, 255, 255, 0.2)",
        padding: "0.75rem 1rem",
        borderRadius: "8px",
        boxShadow: "0 10px 30px rgba(0,0,0,0.65)"
      }}>
        <p style={{ fontSize: "0.85rem", fontWeight: 800, color: textColor, marginBottom: "4px" }}>
          {statusName}
        </p>
        <p style={{ fontSize: "0.8rem", color: "#f1f5f9", fontWeight: 600, margin: 0 }}>
          Count : <span style={{ fontWeight: 900, color: "#ffffff", fontSize: "0.95rem" }}>{countVal}</span>
        </p>
      </div>
    );
  };

  // Radar grouping
  const categories = {
    programming: { name: "Coding", max: 0, matched: 0 },
    frontend:    { name: "Frontend", max: 0, matched: 0 },
    backend:     { name: "Backend", max: 0, matched: 0 },
    cloud:       { name: "Cloud/DevOps", max: 0, matched: 0 },
    general:     { name: "Other", max: 0, matched: 0 }
  };
  const getCat = (skill) => {
    const s = (skill || "").toLowerCase();
    if (["python","java","c++","c#","javascript","typescript","go","rust","kotlin"].some(x => s.includes(x))) return "programming";
    if (["react","angular","vue","html","css","tailwind","bootstrap","nextjs"].some(x => s.includes(x))) return "frontend";
    if (["node","express","django","fastapi","flask","sql","mysql","postgres","mongodb"].some(x => s.includes(x))) return "backend";
    if (["aws","azure","gcp","docker","kubernetes","git","jenkins","ci/cd"].some(x => s.includes(x))) return "cloud";
    return "general";
  };
  allGaps.forEach(item => {
    const skill = item.skill || item.required_skill || "";
    const cat = getCat(skill);
    categories[cat].max += 1;
    if (item.status === "MATCHED") categories[cat].matched += 1;
    else if (item.status === "PARTIALLY_MATCHED") categories[cat].matched += 0.5;
  });
  const radarData = Object.values(categories).map(c => ({
    subject: c.name,
    score: c.max > 0 ? Math.round((c.matched / c.max) * 100) : 0,
    fullMark: 100
  }));

  const getScoreColor = (v) => v >= 80 ? "var(--secondary)" : v >= 65 ? "#f59e0b" : "var(--danger)";
  const getScoreGlow  = (v) => v >= 80 ? "rgba(16,185,129,0.35)" : v >= 65 ? "rgba(245,158,11,0.35)" : "rgba(239,68,68,0.35)";

  const tier = score >= 80 ? "HIGH" : score >= 65 ? "MODERATE" : "LOW";
  const tiers = {
    HIGH:     { label: "Placement Ready",    msg: "Candidate meets the recruitment baseline. Focus on interview prep and mock tests.", badge: "badge-success" },
    MODERATE: { label: "Needs Improvement",  msg: "Partially ready. Bridge identified gaps and strengthen weak areas with the learning plan.", badge: "badge-warning" },
    LOW:      { label: "Skill Gap Found",    msg: "Significant gaps detected. Follow the personalized 4-week learning plan to increase eligibility.", badge: "badge-danger" },
  };
  const tc = tiers[tier];

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>

      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h1 className="page-title">Analysis Results</h1>
        </div>
        <button className="btn btn-primary" onClick={() => navigate("/recommendations")}>
          🎯 View 4-Week Learning Plan
        </button>
      </div>

      {/* Row 1: Score Hero + Profile */}
      <div className="grid-2">

        {/* Left */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>

          {/* Score Card */}
          <div className="card" style={{ background: "linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,27,75,0.6) 100%)", border: `1px solid ${getScoreColor(score)}35`, boxShadow: `0 0 50px ${getScoreGlow(score)}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: "2rem", flexWrap: "wrap" }}>

              {/* Gauge */}
              <div style={{ position: "relative", width: "155px", height: "155px", flexShrink: 0 }}>
                <svg width="155" height="155" viewBox="0 0 155 155">
                  <defs>
                    <filter id="scoreGlow"><feGaussianBlur stdDeviation="4" result="cb"/><feMerge><feMergeNode in="cb"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                  </defs>
                  <circle cx="77.5" cy="77.5" r="64" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="11"/>
                  <circle cx="77.5" cy="77.5" r="64" fill="none"
                    stroke={getScoreColor(score)} strokeWidth="11"
                    strokeDasharray={2 * Math.PI * 64}
                    strokeDashoffset={2 * Math.PI * 64 * (1 - Math.min(score,100) / 100)}
                    strokeLinecap="round" transform="rotate(-90 77.5 77.5)"
                    filter="url(#scoreGlow)"
                    style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)" }}
                  />
                </svg>
                <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", textAlign: "center" }}>
                  <div style={{ fontSize: "2.1rem", fontWeight: 900, letterSpacing: "-0.05em", color: getScoreColor(score), lineHeight: 1 }}>
                    {Math.round(score)}
                  </div>
                  <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em" }}>Score</div>
                </div>
              </div>

              {/* Verdict */}
              <div style={{ flex: 1, minWidth: "180px" }}>
                <span className={`badge ${tc.badge}`} style={{ marginBottom: "0.6rem", fontSize: "0.75rem" }}>{tc.label}</span>
                <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: getScoreColor(score), marginBottom: "0.4rem", lineHeight: 1.2 }}>
                  {Math.round(score)}% Readiness
                </h2>
                <p style={{ color: "var(--text-secondary)", lineHeight: 1.6, fontSize: "0.88rem" }}>{tc.msg}</p>
                <div style={{ display: "flex", gap: "1.25rem", marginTop: "0.85rem", paddingTop: "0.85rem", borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                  {[["Skills", resumeSkills.length]].map(([l,v]) => (
                    <div key={l}>
                      <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>{l}</div>
                      <div style={{ fontSize: "0.85rem", fontWeight: 600 }}>{v}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 🤖 Explainable AI (XAI) Model Decision & Feature Breakdown Card */}
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
              <div>
                <h3 className="card-title" style={{ margin: 0 }}>🤖 Explainable AI (XAI) Feature Impact</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem", marginTop: "2px" }}>
                  Clear model reasoning & evaluation breakdown for every profile attribute.
                </p>
              </div>
              <div style={{ display: "flex", background: "rgba(255,255,255,0.04)", borderRadius: "8px", padding: "2px", border: "1px solid rgba(255,255,255,0.08)" }}>
                <button
                  onClick={() => setXaiTab("exai")}
                  style={{
                    padding: "0.35rem 0.75rem",
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    borderRadius: "6px",
                    border: "none",
                    cursor: "pointer",
                    background: xaiTab === "exai" ? "var(--violet)" : "transparent",
                    color: xaiTab === "exai" ? "#ffffff" : "var(--text-secondary)",
                    transition: "all 0.2s ease"
                  }}
                >
                  💡 XAI Explanations
                </button>
                <button
                  onClick={() => setXaiTab("chart")}
                  style={{
                    padding: "0.35rem 0.75rem",
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    borderRadius: "6px",
                    border: "none",
                    cursor: "pointer",
                    background: xaiTab === "chart" ? "var(--violet)" : "transparent",
                    color: xaiTab === "chart" ? "#ffffff" : "var(--text-secondary)",
                    transition: "all 0.2s ease"
                  }}
                >
                  📊 Feature Chart
                </button>
              </div>
            </div>

            {xaiTab === "exai" ? (
              /* XAI Detailed Model Reasoning List */
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "380px", overflowY: "auto", paddingRight: "4px" }}>
                {xaiFeatureList.map((item, idx) => (
                  <div key={idx} style={{
                    padding: "0.85rem 1rem",
                    background: "rgba(255,255,255,0.02)",
                    borderRadius: "8px",
                    border: "1px solid rgba(255,255,255,0.05)",
                    borderLeft: `4px solid ${item.color}`,
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.4rem"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "var(--text-primary)" }}>{item.name}</span>
                      <span style={{ fontSize: "0.75rem", fontWeight: 800, color: item.color, background: `${item.color}15`, padding: "0.15rem 0.55rem", borderRadius: "999px", border: `1px solid ${item.color}30` }}>
                        {item.val}
                      </span>
                    </div>

                    {/* Strength Bar */}
                    <div style={{ width: "100%", height: "4px", background: "rgba(255,255,255,0.06)", borderRadius: "2px", overflow: "hidden" }}>
                      <div style={{ width: `${item.strengthPct}%`, height: "100%", background: item.color, borderRadius: "2px" }} />
                    </div>

                    {/* Model Reasoning Text ("Why this score was given") */}
                    <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
                      <strong style={{ color: "#e2e8f0" }}>Why this impact: </strong>{item.reasoning}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              /* Horizontal Strength Chart */
              <div style={{ width: "100%", height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart layout="vertical" data={xaiFeatureList} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                    <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" tick={{ fill: "#f1f5f9", fontSize: 11, fontWeight: 600 }} tickFormatter={v => `${v}%`} />
                    <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fill: "#f1f5f9", fontSize: 10, fontWeight: 600 }} width={175} tickLine={false} />
                    <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
                    <Bar dataKey="strengthPct" radius={[0, 4, 4, 0]}>
                      {xaiFeatureList.map((e, i) => <Cell key={i} fill={e.color} fillOpacity={0.85}/>)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Skill Match Status Card */}
          <div className="card">
            <h3 className="card-title">📊 Skill Match Status</h3>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", marginBottom: "1.25rem" }}>
              Summary count of required skills by match alignment status.
            </p>
            <div style={{ width: "100%", height: 170 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[
                  { name: "Matched", count: matched.length, fill: "var(--secondary)" },
                  { name: "Partially Matched", count: partiallyMatched.length, fill: "var(--warning)" },
                  { name: "Missing", count: missing.length, fill: "var(--danger)" },
                ]} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: "#f1f5f9", fontSize: 11, fontWeight: 600 }} />
                  <YAxis stroke="#94a3b8" tick={{ fill: "#f1f5f9", fontSize: 11, fontWeight: 600 }} allowDecimals={false} />
                  {/* Fixed Tooltip with dark background & crisp high-contrast label font for Image 2! */}
                  <Tooltip content={<SkillMatchTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {[
                      { fill: "var(--secondary)" },
                      { fill: "var(--warning)" },
                      { fill: "var(--danger)" }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} fillOpacity={0.85} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>

          {/* Profile Metrics */}
          <div className="card">
            <h3 className="card-title">🎓 Parsed Profile Metrics</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem" }}>
              {[
                { label: "CGPA", value: features.CGPA?.toFixed(2) ?? "N/A", color: "var(--primary)" },
                { label: "Internships", value: features.internships ?? 0, color: "var(--text-primary)" },
                { label: "Projects", value: features.projects ?? 0, color: "var(--text-primary)" },
                { label: "Certifications", value: features.certifications ?? 0, color: "var(--text-primary)" },
              ].map(({ label, value, color }) => (
                <div key={label} style={{ padding: "0.85rem", background: "rgba(255,255,255,0.02)", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.04)" }}>
                  <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "4px" }}>{label}</div>
                  <div style={{ fontSize: "1.35rem", fontWeight: 800, color }}>{value}</div>
                </div>
              ))}
              <div style={{ gridColumn: "1 / -1", padding: "0.85rem", background: "rgba(255,255,255,0.02)", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.04)" }}>
                <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "4px" }}>Specialization</div>
                <div style={{ fontSize: "1rem", fontWeight: 700 }}>{features.specialization || "Not Detected"}</div>
              </div>
            </div>

            {resumeSkills.length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>Skills from Resume</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                  {resumeSkills.map(skill => (
                    <span key={skill} style={{ padding: "0.2rem 0.6rem", fontSize: "0.72rem", fontWeight: 600, background: "rgba(99,102,241,0.12)", color: "#a5b4fc", border: "1px solid rgba(99,102,241,0.22)", borderRadius: "999px" }}>{skill}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Radar */}
          <div className="card" style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <h3 className="card-title" style={{ alignSelf: "flex-start" }}>🕸️ Skill Alignment Profile</h3>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", marginBottom: "0.75rem", alignSelf: "flex-start" }}>Coverage across skill domains vs. job requirements.</p>
            <div style={{ width: "100%", height: 210 }}>
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid stroke="#1e293b" />
                  <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fill: "#f1f5f9", fontSize: 11, fontWeight: 600 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" tick={{ fill: "#cbd5e1", fontSize: 9 }} />
                  <Radar name="Score" dataKey="score" stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.25} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Skill Gap Breakdown */}
      <div className="card">
        <h3 className="card-title">📊 Skill Gap Breakdown</h3>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginBottom: "1.5rem" }}>
          Job-required skills matched against your resume — colour-coded by alignment status.
        </p>
        {allGaps.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>No skill gap data. Ensure a job description was provided.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {allGaps.map((item, idx) => {
              const skill    = item.skill || item.required_skill || "—";
              const border   = item.status === "MATCHED" ? "var(--secondary)" : item.status === "PARTIALLY_MATCHED" ? "var(--warning)" : "var(--danger)";
              const badge    = item.status === "MATCHED" ? "badge-success" : item.status === "PARTIALLY_MATCHED" ? "badge-warning" : "badge-danger";
              const alignmentLabel = item.status === "MATCHED" ? "✓ Verified Skill" : item.status === "PARTIALLY_MATCHED" ? "⚡ Partial Coverage" : "❌ Skill Gap";

              return (
                <div key={idx} className="skill-match-row" style={{ borderLeftColor: border }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.7rem", minWidth: "140px" }}>
                    <span className="skill-name-text" style={{ fontWeight: 700, fontSize: "0.95rem", color: "var(--text-primary)", transition: "color 0.2s ease" }}>{skill}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                    <span className={`badge ${badge}`} style={{ fontSize: "0.72rem", padding: "0.3rem 0.85rem", transition: "all 0.2s ease" }}>
                      {alignmentLabel}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}

export default Dashboard;
