import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import Sidebar from '../components/Sidebar';
import {
  CandidateRow,
  SkillTags,
  StatCard,
  Loader,
  EmptyState,
} from '../components/UI';
import api from '../api/client';

const NAV = [
  { to: '/recruiter',            icon: '🏠', label: 'Dashboard' },
  { to: '/recruiter/post-job',   icon: '➕', label: 'Post Job'   },
  { to: '/recruiter/jobs',       icon: '📋', label: 'My Jobs'    },
];

const RecruiterContext = createContext(null);
export function useRecruiterData() {
  return useContext(RecruiterContext);
}

// ── 1. Recruiter Home Dashboard ─────────────────────────────────
function RecruiterHome() {
  const { jobs, loading } = useRecruiterData();
  const navigate = useNavigate();

  if (loading && !jobs.length) return <Loader text="Loading recruiter dashboard..." />;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Recruiter Control Hub</h1>
          <p>Screen student talent across campus job listings with hybrid AI matching</p>
        </div>
        <button onClick={() => navigate('/recruiter/post-job')} className="btn btn-primary btn-sm">
          ➕ Post New Job Opening
        </button>
      </div>

      <div className="card-grid card-grid-4" style={{ marginBottom: '2rem' }}>
        <StatCard icon="📋" label="Job Postings" value={jobs.length} />
        <StatCard icon="✅" label="Active Listings" value={jobs.length} />
        <StatCard icon="🎯" label="Screening Status" value="Active" />
        <StatCard icon="⚡" label="AI Engine" value="Gemini + FastMatch" />
      </div>

      {jobs.length === 0 ? (
        <EmptyState
          icon="📋"
          title="No Job Postings Yet"
          desc="Create a job description to automatically screen and rank registered student applicants."
          action={
            <button onClick={() => navigate('/recruiter/post-job')} className="btn btn-primary">
              Post New Job →
            </button>
          }
        />
      ) : (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--color-text)' }}>Recent Job Listings</h3>
            <button onClick={() => navigate('/recruiter/jobs')} className="btn btn-outline btn-sm">
              View All Postings →
            </button>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Required Competencies</th>
                  <th>Created Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {jobs.slice(0, 8).map((job) => (
                  <tr key={job.id}>
                    <td style={{ fontWeight: 700, color: 'var(--color-text)' }}>{job.title}</td>
                    <td>
                      <span className="company-badge">
                        🏢 {job.company_name || 'Enterprise'}
                      </span>
                    </td>
                    <td>
                      <SkillTags skills={(job.skills_required || []).slice(0, 4)} variant="neutral" />
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                      {job.created_at ? new Date(job.created_at).toLocaleDateString() : 'Active'}
                    </td>
                    <td>
                      <button
                        onClick={() => navigate('/recruiter/jobs')}
                        className="btn btn-brand-outline btn-sm"
                      >
                        Screen Candidates →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ── 2. Post Job ─────────────────────────────────────────────────
function PostJob() {
  const { refreshJobs } = useRecruiterData();
  const [form, setForm] = useState({ title: '', company_name: '', description: '', skills_required: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) {
      toast.error('Please enter a title and description');
      return;
    }

    setLoading(true);
    try {
      await api.post('/jobs', {
        title: form.title,
        company_name: form.company_name || null,
        description: form.description,
        skills_required: form.skills_required.split(',').map((s) => s.trim()).filter(Boolean),
      });
      toast.success('Job posted & candidate screening complete! 🎉');
      await refreshJobs();
      navigate('/recruiter/jobs');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to post job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Create Job Listing</h1>
          <p>Publish a campus opening to instantly match and rank candidate resumes</p>
        </div>
      </div>

      <div className="card" style={{ maxWidth: 720 }}>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Role / Job Title *</label>
              <input
                name="title"
                value={form.title}
                onChange={handleChange}
                className="input"
                placeholder="e.g. SDE 1 - Backend"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Hiring Company Name</label>
              <input
                name="company_name"
                value={form.company_name}
                onChange={handleChange}
                className="input"
                placeholder="e.g. TCS, Zoho, Cognizant, Wipro"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Key Required Skills (comma-separated)</label>
            <input
              name="skills_required"
              value={form.skills_required}
              onChange={handleChange}
              className="input"
              placeholder="e.g. React, Node.js, Python, PostgreSQL, Docker"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Full Job Description & Criteria *</label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              className="textarea"
              rows={7}
              placeholder="Describe candidate responsibilities, qualifications, and project expectations..."
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }}
          >
            {loading ? 'Screening Candidates...' : 'Publish Job & Screen All Candidates →'}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── 3. My Jobs & Ranked Candidates ──────────────────────────────
function MyJobs() {
  const { jobs, loading } = useRecruiterData();
  const [selectedJob, setSelectedJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [interviewQuestions, setInterviewQuestions] = useState(null);
  const [candidateNameForQuestions, setCandidateNameForQuestions] = useState('');
  const [loadingQuestions, setLoadingQuestions] = useState(false);

  useEffect(() => {
    if (jobs.length > 0 && !selectedJob) {
      loadCandidates(jobs[0]);
    }
  }, [jobs]);

  const loadCandidates = async (job) => {
    setSelectedJob(job);
    setInterviewQuestions(null);
    setLoadingCandidates(true);
    try {
      const { data } = await api.get(`/jobs/${job.id}/candidates`);
      setCandidates(data);
    } catch {
      toast.error('Could not fetch candidate rankings');
    } finally {
      setLoadingCandidates(false);
    }
  };

  const shortlistCandidate = async (jobId, studentId) => {
    try {
      await api.post(`/jobs/${jobId}/shortlist`, { student_id: studentId, status: 'shortlisted' });
      toast.success('Candidate shortlisted! ⭐');
    } catch {
      toast.error('Shortlist update failed');
    }
  };

  const loadInterviewQuestions = async (studentId, jobId, name) => {
    setCandidateNameForQuestions(name);
    setLoadingQuestions(true);
    setInterviewQuestions(null);
    try {
      const { data } = await api.get(`/candidates/${studentId}/interview-questions?job_id=${jobId}`);
      setInterviewQuestions(data.questions || []);
    } catch {
      toast.error('Could not generate interview questions');
    } finally {
      setLoadingQuestions(false);
    }
  };

  if (loading && !jobs.length) return <Loader text="Loading job listings..." />;
  if (!jobs.length) return <EmptyState icon="📋" title="No job listings found" desc="Create your first job listing to see candidate rankings." />;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Candidate Rankings & Screening</h1>
          <p>AI-ranked candidate pool ordered by semantic compatibility and technical skill overlap</p>
        </div>
      </div>

      {/* Job Selection Tabs / Pill Selector */}
      <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap', marginBottom: '1.75rem' }}>
        {jobs.map((job) => {
          const isSelected = selectedJob?.id === job.id;
          return (
            <button
              key={job.id}
              onClick={() => loadCandidates(job)}
              className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-outline'}`}
            >
              {job.company_name ? `${job.company_name} - ` : ''}{job.title}
            </button>
          );
        })}
      </div>

      {selectedJob && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                  <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--color-text)' }}>{selectedJob.title}</h3>
                  {selectedJob.company_name && (
                    <span className="company-badge">🏢 {selectedJob.company_name}</span>
                  )}
                </div>
                <div style={{ marginTop: '0.5rem' }}>
                  <SkillTags skills={selectedJob.skills_required} variant="neutral" />
                </div>
              </div>
              <span className="fit-badge fit-high tabular-score" style={{ fontSize: '0.85rem' }}>
                {candidates.length} Registered Candidates Screened
              </span>
            </div>
          </div>

          {loadingCandidates ? (
            <Loader text="Calculating candidate compatibility fit..." />
          ) : candidates.length === 0 ? (
            <EmptyState
              icon="👤"
              title="No Candidates Found"
              desc="Candidates will automatically appear here once students upload resumes matching this role."
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {candidates.map((c) => (
                <CandidateRow
                  key={c.student_id}
                  rank={c.rank}
                  title={c.name}
                  subtitle={`${c.department || 'Department not specified'} • CGPA: ${c.cgpa ?? '—'}`}
                  score={c.final_score}
                  matchedSkills={c.matched_skills || []}
                  missingSkills={c.missing_skills || []}
                  extraActions={
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className="btn btn-sm btn-outline"
                        onClick={() => shortlistCandidate(selectedJob.id, c.student_id)}
                      >
                        ⭐ Shortlist
                      </button>
                      <button
                        className="btn btn-sm btn-brand-outline"
                        onClick={() => loadInterviewQuestions(c.student_id, selectedJob.id, c.name)}
                      >
                        ❓ Questions
                      </button>
                    </div>
                  }
                />
              ))}
            </div>
          )}

          {/* Interview Questions Modal / Drawer */}
          {(loadingQuestions || interviewQuestions) && (
            <div className="card fade-in" style={{ marginTop: '1rem', border: '1px solid var(--color-action)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h4 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--color-text)' }}>
                  Tailored Interview Questions for {candidateNameForQuestions}
                </h4>
                <button
                  onClick={() => setInterviewQuestions(null)}
                  className="btn btn-sm btn-outline"
                >
                  ✕ Close
                </button>
              </div>

              {loadingQuestions ? (
                <Loader text="Generating tailored interview questions with Gemini..." />
              ) : (
                <ol style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {interviewQuestions.map((q, idx) => (
                    <li key={idx} style={{ fontSize: '0.925rem', color: 'var(--color-text)', lineHeight: 1.5 }}>
                      {q}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Root Recruiter Dashboard Layout ─────────────────────────────
export default function RecruiterDashboardLayout() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = useCallback(async () => {
    try {
      const { data } = await api.get('/jobs');
      setJobs(data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const value = {
    jobs,
    loading,
    refreshJobs: fetchJobs,
  };

  return (
    <RecruiterContext.Provider value={value}>
      <div className="app-layout">
        <Sidebar links={NAV} />
        <div className="main-content">
          <Routes>
            <Route index element={<RecruiterHome />} />
            <Route path="post-job" element={<PostJob />} />
            <Route path="jobs"     element={<MyJobs />} />
            <Route path="*"        element={<Navigate to="/recruiter" replace />} />
          </Routes>
        </div>
      </div>
    </RecruiterContext.Provider>
  );
}
