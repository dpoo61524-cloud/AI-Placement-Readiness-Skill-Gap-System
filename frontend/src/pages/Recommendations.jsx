import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Recommendations({ analysisResult }) {
  const navigate = useNavigate();
  const recommendation_plan = analysisResult?.recommendation_plan || {};
  const weeks = recommendation_plan.weeks || [];
  const project_difficulty_level = recommendation_plan.project_difficulty_level || "intermediate";
  const [activeWeek, setActiveWeek] = useState(0);

  // Extract Capstone Project from Week 4 with domain awareness
  const primarySkillTag = weeks[0]?.focus_skill?.toLowerCase() || "excel";
  
  const getFallbackCapstone = (skill) => {
    if (skill.includes("communication") || skill.includes("presentation") || skill.includes("soft")) {
      return {
        title: "Corporate Communication & Executive Presentation Portfolio",
        provider: "Self-Guided Professional Project",
        difficulty: project_difficulty_level,
        description: "Develop a comprehensive professional communication portfolio including executive proposals, slide decks, and technical project presentation walkthroughs.",
        link: "https://github.com/topics/presentation-deck",
        skill_tag: "communication"
      };
    }
    return {
      title: "Executive Financial & Sales Analytics Dashboard in Microsoft Excel",
      provider: "Self-Guided Analytics Project",
      difficulty: project_difficulty_level,
      description: "Build an automated sales reporting dashboard using Power Query, Pivot Tables, XLOOKUP, data validation, and interactive slicers.",
      link: "https://github.com/topics/excel-dashboard",
      skill_tag: "excel"
    };
  };

  const rawCapstone = weeks.find(w => w.week === 4)?.suggested_project;
  const isInvalidCapstone = !rawCapstone || (primarySkillTag.includes("excel") || primarySkillTag.includes("communication")) && rawCapstone.title.toLowerCase().includes("full-stack");
  const capstone_project = isInvalidCapstone ? getFallbackCapstone(primarySkillTag) : rawCapstone;

  // Extract Certifications from Week 3 resources with strict title deduplication & domain filtering
  const rawCerts = weeks.find(w => w.week === 3)?.resources || [];
  const seenCerts = new Set();
  let suggested_certifications = rawCerts.filter(c => {
    if (!c.title || seenCerts.has(c.title)) return false;
    // Strictly filter out Java Developer certifications if target is not Java
    if (!primarySkillTag.includes("java") && c.title.toLowerCase().includes("java")) {
      return false;
    }
    seenCerts.add(c.title);
    return true;
  });

  // Fallback domain-accurate certifications for Data Analytics / Excel / Communication
  if (suggested_certifications.length === 0) {
    if (primarySkillTag.includes("excel") || primarySkillTag.includes("excle") || primarySkillTag.includes("data")) {
      suggested_certifications = [
        {
          title: "Microsoft Office Specialist: Excel Expert (MO-201)",
          provider: "Microsoft",
          link: "https://learn.microsoft.com/en-us/credentials/certifications/mos-excel-expert-2019"
        },
        {
          title: "Microsoft Certified: Power BI Data Analyst Associate (PL-300)",
          provider: "Microsoft",
          link: "https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/"
        }
      ];
    } else if (primarySkillTag.includes("communication") || primarySkillTag.includes("presentation")) {
      suggested_certifications = [
        {
          title: "Professional Business Communication & Executive Presence Certificate",
          provider: "Coursera (Wharton School)",
          link: "https://www.coursera.org/learn/wharton-communication-skills"
        }
      ];
    } else {
      suggested_certifications = [
        {
          title: "Google Data Analytics Professional Certificate",
          provider: "Coursera (Google)",
          link: "https://www.coursera.org/professional-certificates/google-data-analytics"
        }
      ];
    }
  }

  const getDifficultyColor = (diff) => {
    if (!diff) return "badge-warning";
    const d = diff.toLowerCase();
    if (d.includes("easy") || d.includes("beginner")) return "badge-success";
    if (d.includes("hard") || d.includes("advanced")) return "badge-danger";
    return "badge-warning";
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h1 className="page-title">Personalized Learning Plan</h1>
          <p style={{ color: "var(--text-secondary)", marginTop: "0.25rem" }}>Optimized weekly training schedule designed to bridge your skill gaps.</p>
        </div>
        <button className="btn btn-secondary" onClick={() => navigate("/dashboard")}>
          ⬅ Back to Analytics
        </button>
      </div>

      <div className="grid-2">
        
        {/* Left Side: 4-Week Schedule */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "0.5rem" }}>📅 Weekly Syllabus & Schedule</h2>
          
          {weeks.map((week, idx) => {
            const isOpen = activeWeek === idx;
            const focusSkillTag = (week.focus_skill || "").toLowerCase();
            
            // Dynamic topics
            let displayTopics = week.learning_objectives || [];
            
            // Dynamic resources
            let displayResources = week.resources || [];
            if (focusSkillTag.includes("communication") || focusSkillTag.includes("presentation") || focusSkillTag.includes("soft")) {
              displayResources = displayResources.filter(r => {
                const text = (r.title + " " + (r.description || "") + " " + (r.skill_tag || "")).toLowerCase();
                return !text.includes("excel") && !text.includes("microsoft office") && !text.includes("power bi") && !text.includes("java") && !text.includes("c++");
              });
            } else if (focusSkillTag.includes("excel") || focusSkillTag.includes("excle") || focusSkillTag.includes("spreadsheet")) {
              displayResources = displayResources.filter(r => {
                const text = (r.title + " " + (r.description || "") + " " + (r.skill_tag || "")).toLowerCase();
                return !text.includes("communication skills") && !text.includes("public speaking") && !text.includes("java programming");
              });
            }

            if (displayResources.length === 0) {
              if (focusSkillTag.includes("excel") || focusSkillTag.includes("excle") || focusSkillTag.includes("spreadsheet")) {
                displayResources = [
                  {
                    title: "Excel Skills for Business Specialization",
                    provider: "Coursera (Macquarie University)",
                    difficulty: "easy",
                    description: "Master Excel formulas, VLOOKUP/XLOOKUP, data validation, conditional formatting, and dashboard design.",
                    link: "https://www.coursera.org/specializations/excel",
                    resource_type: "course"
                  },
                  {
                    title: "Microsoft Excel Tutorial for Beginners - Full Course",
                    provider: "freeCodeCamp",
                    difficulty: "easy",
                    description: "Comprehensive tutorial covering Excel basics, functions, charts, pivot tables, and data analysis techniques.",
                    link: "https://www.youtube.com/watch?v=Vl0H-qTclOg",
                    resource_type: "youtube"
                  }
                ];
              } else if (focusSkillTag.includes("communication") || focusSkillTag.includes("presentation")) {
                displayResources = [
                  {
                    title: "Improving Communication Skills",
                    provider: "Coursera (University of Pennsylvania)",
                    difficulty: "easy",
                    description: "Learn active listening, persuasive speaking, structuring messages, and managing workplace conflicts.",
                    link: "https://www.coursera.org/learn/wharton-communication-skills",
                    resource_type: "course"
                  },
                  {
                    title: "How to Speak Confidently & Influence Others",
                    provider: "Ted Talks Playlist",
                    difficulty: "easy",
                    description: "A collection of 10 expert presentations on body language, speech formatting, and public presenting tips.",
                    link: "https://www.youtube.com/",
                    resource_type: "youtube"
                  }
                ];
              }
            }

            const focusTitle = week.focus_skill ? week.focus_skill.toUpperCase() : `WEEK ${week.week}`;

            return (
              <div key={idx} className="accordion" style={{ borderColor: isOpen ? "var(--primary)" : "var(--border-color)" }}>
                <div 
                  className="accordion-header" 
                  onClick={() => setActiveWeek(isOpen ? null : idx)}
                  style={{ backgroundColor: isOpen ? "rgba(124, 58, 237, 0.04)" : "transparent" }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                    <span className="badge badge-info" style={{ borderRadius: "4px" }}>
                      Week {week.week}
                    </span>
                    <strong style={{ fontSize: "1rem", color: isOpen ? "var(--primary-light)" : "var(--text-primary)" }}>
                      Focus: {focusTitle} {week.topic ? `(${week.topic})` : ""}
                    </strong>
                  </div>
                  <span style={{ fontSize: "0.8rem", transform: isOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>
                    ▼
                  </span>
                </div>

                {isOpen && (
                  <div className="accordion-content">
                    <div style={{ marginBottom: "1.25rem" }}>
                      <h4 style={{ fontSize: "0.72rem", color: "var(--text-secondary)", textTransform: "uppercase", marginBottom: "0.4rem", fontWeight: 700, letterSpacing: "0.05em" }}>
                        Topics to Master
                      </h4>
                      <p style={{ fontSize: "0.92rem", color: "var(--text-primary)", lineHeight: 1.6 }}>
                        {displayTopics.join(", ")}
                      </p>
                    </div>

                    {week.coach_tip && (
                      <div className="coach-tip">
                        <h4 style={{ fontSize: "0.75rem", color: "var(--violet-light)", textTransform: "uppercase", marginBottom: "0.2rem", fontWeight: 700, letterSpacing: "0.05em" }}>
                          💡 Coach Recommendation
                        </h4>
                        <p style={{ fontSize: "0.88rem", color: "var(--text-primary)", fontStyle: "italic" }}>
                          "{week.coach_tip}"
                        </p>
                      </div>
                    )}

                    <div>
                      <h4 style={{ fontSize: "0.72rem", color: "var(--text-secondary)", textTransform: "uppercase", marginBottom: "0.5rem", fontWeight: 700, letterSpacing: "0.05em" }}>
                        Recommended Resources
                      </h4>
                      
                      <div className="resources-grid">
                        {displayResources.map((res, rIdx) => (
                          <div key={rIdx} className="resource-item-card">
                            <div className="resource-header">
                              <a 
                                href={res.link} 
                                target="_blank" 
                                rel="noopener noreferrer" 
                                className="resource-title"
                              >
                                🔗 {res.title}
                              </a>
                              <span className={`badge ${getDifficultyColor(res.difficulty)}`}>
                                {res.difficulty}
                              </span>
                            </div>
                            
                            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                              {res.description}
                            </p>
                            
                            <div className="resource-meta">
                              <span>Type: <strong>{res.resource_type.toUpperCase()}</strong></span>
                              <span>•</span>
                              <span>Provider: <strong>{res.provider}</strong></span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right Side: Capstone &Suggested Certifications */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* Capstone Project */}
          <div className="card highlight">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h3 className="card-title" style={{ margin: 0 }}>🛠️ Capstone Project Suggestion</h3>
              <span className={`badge ${getDifficultyColor(capstone_project.difficulty)}`}>
                {capstone_project.difficulty}
              </span>
            </div>
            
            <h4 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--violet-light)", marginBottom: "0.5rem" }}>
              {capstone_project.title}
            </h4>
            
            <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", lineHeight: 1.6, marginBottom: "1.25rem" }}>
              {capstone_project.description}
            </p>

            <div style={{ background: "rgba(255,255,255,0.02)", padding: "0.85rem", borderRadius: "8px", borderLeft: "3px solid var(--violet)" }}>
              <span style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>
                Target Domain Focus
              </span>
              <p style={{ fontSize: "0.85rem", fontWeight: 600, marginTop: "2px" }}>
                {capstone_project.skill_tag ? capstone_project.skill_tag.toUpperCase() : "GENERAL"}
              </p>
            </div>
            
            {capstone_project.link && (
              <div style={{ marginTop: "1rem" }}>
                <a href={capstone_project.link} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ width: "100%" }}>
                  View Project Repository ↗
                </a>
              </div>
            )}
          </div>

          {/* Certifications */}
          <div className="card">
            <h3 className="card-title">📜 Recommended Certifications</h3>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", marginBottom: "1.25rem" }}>
              Validate your skills and significantly boost candidate ranking index.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
              {suggested_certifications.length > 0 ? (
                suggested_certifications.map((cert, index) => (
                  <div 
                    key={index} 
                    style={{ 
                      padding: "0.75rem", 
                      background: "rgba(255,255,255,0.02)", 
                      border: "1px solid var(--border-color)", 
                      borderRadius: "8px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}
                  >
                    <div style={{ display: "flex", flexDirection: "column" }}>
                      <span style={{ fontWeight: 600, fontSize: "0.88rem" }}>{cert.title}</span>
                      <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>Authority: {cert.provider}</span>
                    </div>
                    <a href={cert.link} target="_blank" rel="noopener noreferrer" className="badge badge-cyan" style={{ fontSize: "0.65rem", textDecoration: "none" }}>
                      Register ↗
                    </a>
                  </div>
                ))
              ) : (
                <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontStyle: "italic" }}>
                  No target certifications suggested. Focus on core lessons.
                </p>
              )}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Recommendations;
