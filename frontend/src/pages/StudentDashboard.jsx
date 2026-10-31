import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import Sidebar from '../components/Sidebar';
import {
  FitBar,
  CandidateRow,
  SkillTags,
  StatCard,
  Loader,
  EmptyState,
} from '../components/UI';
import api from '../api/client';

const NAV = [
  { to: '/student',           icon: '🏠', label: 'Dashboard'   },
  { to: '/student/resume',    icon: '📄', label: 'My Resume'   },
  { to: '/student/matches',   icon: '🎯', label: 'Job Matches' },
  { to: '/student/profile',   icon: '👤', label: 'Profile'     },
];

const StudentContext = createContext(null);
export function useStudentData() {
  return useContext(StudentContext);
}

// ── 1. Dashboard View ───────────────────────────────────────────
function DashboardHome() {
  const { matches, profile, loading } = useStudentData();
  const navigate = useNavigate();

  if (loading && !matches.length && !profile) return <Loader text="Loading candidate dashboard..." />;

  const bestMatch = matches[0];
  const avgScore = matches.length
    ? (matches.reduce((sum, m) => sum + (Number(m.final_score) || 0), 0) / matches.length).toFixed(1)
    : 0;

  const skillsCount = profile?.parsed_json?.skills?.length || 0;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Student Placement Hub</h1>
          <p>Placement readiness, AI profile screening, and corporate job recommendations</p>
        </div>
        <button onClick={() => navigate('/student/resume')} className="btn btn-primary btn-sm">
          📄 Upload / Update Resume
        </button>
      </div>

      <div className="card-grid card-grid-4" style={{ marginBottom: '2rem' }}>
        <StatCard icon="🎯" label="Matched Jobs" value={matches.length} />
        <StatCard icon="⭐" label="Top Fit Score" value={bestMatch ? `${Math.round(bestMatch.final_score)}%` : '—'} />
        <StatCard icon="📊" label="Avg Match Fit" value={matches.length ? `${avgScore}%` : '—'} />
        <StatCard icon="🔑" label="Skills Detected" value={skillsCount} />
      </div>

      {bestMatch ? (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.4rem' }}>
                <span className="fit-badge fit-high">
                  ★ TOP RECOMMENDED POSITION
                </span>
                {bestMatch.job?.company_name && (
                  <span className="company-badge">
                    🏢 {bestMatch.job.company_name}
                  </span>
                )}
              </div>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--color-text)' }}>
                {bestMatch.job?.title || `Position #${bestMatch.job_id}`}
              </h2>
            </div>
            <button
              onClick={() => navigate('/student/matches')}
              className="btn btn-primary btn-sm"
            >
              View All {matches.length} Matches →
            </button>
          </div>

          {/* Horizontal Fit Bar */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
              Overall Compatibility Fit
            </div>
            <FitBar score={bestMatch.final_score} />
          </div>

          <p style={{ fontSize: '0.925rem', color: 'var(--color-text-secondary)', marginBottom: '1.25rem', lineHeight: 1.6 }}>
            {bestMatch.explanation}
          </p>

          <div className="skills-chips-row">
            <div className="chips-group">
              <span className="chips-label">Matched:</span>
              {(bestMatch.matched_skills || []).map((s, i) => (
                <span key={i} className="chip chip-matched">✓ {s}</span>
              ))}
              {(!bestMatch.matched_skills || bestMatch.matched_skills.length === 0) && (
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None recorded</span>
              )}
            </div>
            {(bestMatch.missing_skills || []).length > 0 && (
              <div className="chips-group">
                <span className="chips-label">Missing:</span>
                {bestMatch.missing_skills.map((s, i) => (
                  <span key={i} className="chip chip-missing">✕ {s}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <EmptyState
          icon="📄"
          title="No Job Matches Yet"
          desc="Upload your resume to receive instantaneous AI screening and matching against active corporate placement openings."
          action={
            <button onClick={() => navigate('/student/resume')} className="btn btn-primary">
              Upload Resume Now →
            </button>
          }
        />
      )}
    </div>
  );
}

// ── 2. Resume Upload View ───────────────────────────────────────
function ResumeUpload() {
  const { profile, refreshData } = useStudentData();
  const [loading, setLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (files) => {
    if (!files || !files[0]) return;
    setLoading(true);
    setUploadResult(null);

    const fd = new FormData();
    fd.append('file', files[0]);

    try {
      const { data } = await api.post('/students/resume', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadResult(data);
      toast.success('Resume analyzed & job matches updated! 🎉');
      await refreshData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Resume upload failed');
    } finally {
      setLoading(false);
    }
  }, [refreshData]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  const parsed = uploadResult?.parsed_info || profile?.parsed_json || {};
  const hasResume = Boolean(profile?.resume_path || uploadResult);

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Resume Screening & Skill Extraction</h1>
          <p>Instant parsing with PyMuPDF and AI skill matching against 25+ top Indian tech employers</p>
        </div>
      </div>

      <div className="card-grid card-grid-2">
        {/* Upload Box */}
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--color-text)' }}>
            {hasResume ? 'Update Your Resume' : 'Upload Resume File'}
          </h3>
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <div className="dropzone-icon">📁</div>
            <div className="dropzone-text">
              {isDragActive ? (
                <strong style={{ color: 'var(--color-text)' }}>Drop your file here!</strong>
              ) : (
                <>
                  <strong style={{ color: 'var(--color-text)' }}>Drag & drop your resume</strong> or <strong>click to browse</strong>
                </>
              )}
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
                Supports PDF, DOCX, TXT • Lightning-fast extraction
              </div>
            </div>
          </div>

          {loading && (
            <div style={{ marginTop: '1.5rem' }}>
              <Loader text="Screening and extracting competencies with AI..." />
            </div>
          )}

          {uploadResult && (
            <div style={{ marginTop: '1.5rem', padding: '1.25rem', background: 'var(--color-surface-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--fit-high)', fontWeight: 700, marginBottom: '0.5rem' }}>
                <span>✓</span> {uploadResult.message}
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '1.25rem' }}>
                Extracted {uploadResult.skills_extracted} technical and professional skills in {uploadResult.performance?.total_ms || 120}ms.
              </p>
              <button
                onClick={() => navigate('/student/matches')}
                className="btn btn-primary btn-sm"
                style={{ width: '100%', justifyContent: 'center' }}
              >
                Explore Top Job Matches →
              </button>
            </div>
          )}
        </div>

        {/* Current Parsed Profile State */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--color-text)' }}>Active Resume Status</h3>
            <span className={`fit-badge ${hasResume ? 'fit-high' : 'fit-low'}`}>
              {hasResume ? '✓ Active Resume' : '✕ No Resume'}
            </span>
          </div>

          {hasResume ? (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>
                  Detected Competencies ({parsed.skills?.length || 0})
                </div>
                <SkillTags skills={parsed.skills} variant="neutral" />
              </div>

              {parsed.summary && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.4rem' }}>
                    Executive Summary
                  </div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: 1.6, background: 'var(--color-surface-subtle)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    {parsed.summary}
                  </p>
                </div>
              )}

              {parsed.education?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.4rem' }}>
                    Academic Background
                  </div>
                  {parsed.education.map((edu, idx) => (
                    <div key={idx} style={{ fontSize: '0.875rem', marginBottom: '0.4rem', color: 'var(--color-text)' }}>
                      <strong>{edu.degree || edu}</strong> {edu.institution ? `• ${edu.institution}` : ''} {edu.cgpa ? `(CGPA: ${edu.cgpa})` : ''}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--color-text-secondary)' }}>
              <p>No resume uploaded yet. Use the upload box on the left to start.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── 3. Job Matches View ─────────────────────────────────────────
function JobMatches() {
  const { matches, loading } = useStudentData();
  const [selectedJob, setSelectedJob] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const navigate = useNavigate();

  const loadSuggestions = async (jobId) => {
    if (selectedJob === jobId) {
      setSelectedJob(null);
      setSuggestions(null);
      return;
    }
    setSelectedJob(jobId);
    setLoadingSuggestions(true);
    try {
      const { data } = await api.get(`/students/me/suggestions/${jobId}`);
      setSuggestions(data);
    } catch {
      toast.error('Could not load detailed suggestions');
    } finally {
      setLoadingSuggestions(false);
    }
  };

  if (loading && !matches.length) return <Loader text="Loading your corporate job matches..." />;

  if (!matches.length) {
    return (
      <div className="fade-in">
        <div className="page-header">
          <h1>Ranked Job Matches</h1>
        </div>
        <EmptyState
          icon="🎯"
          title="No Matches Found"
          desc="Please upload your resume to generate tailored job compatibility scores."
          action={
            <button onClick={() => navigate('/student/resume')} className="btn btn-primary">
              Upload Resume →
            </button>
          }
        />
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Ranked Job Matches</h1>
          <p>{matches.length} active corporate positions evaluated • sorted by highest compatibility fit</p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {matches.map((m, index) => {
          const isSelected = selectedJob === m.job_id;
          const jobTitle = m.job?.title || `Position #${m.job_id}`;
          const companyName = m.job?.company_name || null;

          return (
            <div key={m.id || index} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <CandidateRow
                rank={index + 1}
                title={jobTitle}
                company={companyName}
                subtitle={`ATS Keyword Fit: ${Math.round(m.ats_score || 0)}% • Semantic Fit: ${Math.round(m.semantic_score)}% • Rule Overlap: ${Math.round(m.rule_score)}%`}
                score={m.final_score}
                matchedSkills={m.matched_skills || []}
                missingSkills={m.missing_skills || []}
                extraActions={
                  <button
                    className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-outline'}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      loadSuggestions(m.job_id);
                    }}
                  >
                    {isSelected ? '▲ Hide Analysis' : '🔍 Fit Analysis'}
                  </button>
                }
              />

              {/* Collapsible Deep Analysis */}
              {isSelected && (
                <div
                  className="card fade-in"
                  style={{
                    background: 'var(--color-surface-subtle)',
                    border: '1px solid var(--color-action)',
                    padding: '1.5rem',
                  }}
                >
                  {loadingSuggestions ? (
                    <Loader text="Generating detailed placement analysis..." />
                  ) : suggestions ? (
                    <div>
                      <div className="card-grid card-grid-2" style={{ marginBottom: '1.25rem' }}>
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                            ATS Keyword Match
                          </div>
                          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-action)' }} className="tabular-score">
                            {Math.round(suggestions.ats_score)}%
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                            Final Weighted Score
                          </div>
                          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-text)' }} className="tabular-score">
                            {Math.round(suggestions.final_score)}%
                          </div>
                        </div>
                      </div>

                      {suggestions.explanation && (
                        <div style={{ marginBottom: '1.25rem' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.35rem' }}>
                            AI Suitability Assessment
                          </div>
                          <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                            {suggestions.explanation}
                          </p>
                        </div>
                      )}

                      {suggestions.improvement_suggestions?.length > 0 && (
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>
                            Targeted Resume Improvement Recommendations
                          </div>
                          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {suggestions.improvement_suggestions.map((tip, i) => (
                              <li key={i} style={{ fontSize: '0.875rem', color: 'var(--color-text)', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                                <span style={{ color: 'var(--color-action)', fontWeight: 700 }}>→</span>
                                <span>{tip}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── 4. Profile View ─────────────────────────────────────────────
function ProfileView() {
  const { profile, loading } = useStudentData();

  if (loading && !profile) return <Loader text="Loading profile..." />;
  if (!profile) return <EmptyState icon="👤" title="Profile Not Found" />;

  const parsed = profile.parsed_json || {};

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Student Profile</h1>
          <p>Academic credentials and verified technical skills</p>
        </div>
      </div>

      <div className="card-grid card-grid-2">
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, marginBottom: '1.25rem', color: 'var(--color-text)' }}>Academic Details</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>Department:</span>
              <div style={{ fontWeight: 700, color: 'var(--color-text)', fontSize: '1rem' }}>{profile.department || 'Not specified'}</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>CGPA:</span>
              <div style={{ fontWeight: 700, color: 'var(--color-text)', fontSize: '1rem' }} className="tabular-score">{profile.cgpa ?? 'Not specified'}</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>Resume Status:</span>
              <div style={{ marginTop: '0.25rem' }}>
                <span className={`fit-badge ${profile.resume_path ? 'fit-high' : 'fit-low'}`}>
                  {profile.resume_path ? '✓ Verified on File' : '✕ No Resume Uploaded'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, marginBottom: '1.25rem', color: 'var(--color-text)' }}>Extracted Skills</h3>
          <SkillTags skills={parsed.skills} variant="neutral" />
        </div>
      </div>
    </div>
  );
}

// ── Root Student Dashboard Layout ───────────────────────────────
export default function StudentDashboardLayout() {
  const [profile, setProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [profRes, matchRes] = await Promise.allSettled([
        api.get('/students/me'),
        api.get('/students/me/matches'),
      ]);

      if (profRes.status === 'fulfilled') setProfile(profRes.value.data);
      if (matchRes.status === 'fulfilled') setMatches(matchRes.value.data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const contextValue = {
    profile,
    matches,
    loading,
    refreshData: loadData,
  };

  return (
    <StudentContext.Provider value={contextValue}>
      <div className="app-layout">
        <Sidebar links={NAV} />
        <div className="main-content">
          <Routes>
            <Route index element={<DashboardHome />} />
            <Route path="resume"  element={<ResumeUpload />} />
            <Route path="matches" element={<JobMatches />} />
            <Route path="profile" element={<ProfileView />} />
            <Route path="*"       element={<Navigate to="/student" replace />} />
          </Routes>
        </div>
      </div>
    </StudentContext.Provider>
  );
}
