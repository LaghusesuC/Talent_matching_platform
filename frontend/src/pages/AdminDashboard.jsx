import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';
import Sidebar from '../components/Sidebar';
import { StatCard, Loader, EmptyState, SkillTags, getFitTier } from '../components/UI';
import api from '../api/client';

const NAV = [
  { to: '/admin',            icon: '🏠', label: 'Dashboard'  },
  { to: '/admin/companies',  icon: '🏢', label: 'Companies'  },
  { to: '/admin/students',   icon: '🎓', label: 'Students'   },
  { to: '/admin/users',      icon: '👥', label: 'Users'      },
  { to: '/admin/reports',    icon: '📊', label: 'Reports'    },
];

const CHART_COLORS = ['#6366F1', '#06B6D4', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6'];

const AdminContext = createContext(null);
export function useAdminData() {
  return useContext(AdminContext);
}

// ── 1. Admin Home / Analytics ───────────────────────────────────
function AdminHome() {
  const { analytics, loading, refreshAnalytics } = useAdminData();
  const [seeding, setSeeding] = useState(false);

  const seedJobs = async () => {
    setSeeding(true);
    try {
      const { data } = await api.post('/admin/seed-jobs');
      toast.success(`${data.total_created} Indian company jobs seeded! 🚀`);
      if (data.skipped?.length) {
        toast(`${data.total_skipped} jobs already existed (skipped)`, { icon: 'ℹ️' });
      }
      await refreshAnalytics();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to seed jobs');
    } finally {
      setSeeding(false);
    }
  };

  if (loading && !analytics) return <Loader text="Loading placement analytics..." />;
  if (!analytics) return <EmptyState icon="📊" title="No analytics available" />;

  const barData = (analytics.top_jobs || []).map((j) => ({
    name: j.title.length > 18 ? j.title.slice(0, 16) + '...' : j.title,
    applicants: j.applicants,
  }));

  const pieData = [
    { name: 'Students', value: analytics.total_students || 0 },
    { name: 'Recruiters', value: analytics.total_recruiters || 0 },
  ];

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Campus Placement Analytics</h1>
          <p>Institutional oversight, recruitment funnel, and match statistics</p>
        </div>
        <button
          className="btn btn-primary btn-sm"
          onClick={seedJobs}
          disabled={seeding}
          title="Seed predefined job openings from leading Indian companies"
        >
          {seeding ? 'Seeding Indian Companies...' : '🌱 Seed Indian Company Jobs'}
        </button>
      </div>

      <div className="card-grid card-grid-4" style={{ marginBottom: '2rem' }}>
        <StatCard icon="🎓" label="Enrolled Students" value={analytics.total_students} />
        <StatCard icon="🏢" label="Recruiting Partners" value={analytics.total_recruiters} />
        <StatCard icon="📋" label="Job Openings" value={analytics.total_jobs} />
        <StatCard icon="🔗" label="AI Matches Formed" value={analytics.total_matches} />
        <StatCard icon="⭐" label="Candidates Shortlisted" value={analytics.total_shortlists} />
        <StatCard icon="📈" label="Avg Candidate Fit" value={`${analytics.avg_final_score}%`} />
        <StatCard icon="📝" label="Avg ATS Score" value={`${analytics.avg_ats_score}%`} />
        <StatCard icon="⚡" label="Placement Health" value="Optimal" />
      </div>

      <div className="card-grid card-grid-2">
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, marginBottom: '1.25rem', color: 'var(--color-text)' }}>
            Top Job Openings by Applicant Volume
          </h3>
          {barData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-surface)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 8,
                    color: 'var(--color-text)',
                    fontFamily: 'Plus Jakarta Sans',
                    boxShadow: 'var(--shadow-card)',
                  }}
                />
                <Bar dataKey="applicants" fill="var(--color-action)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState icon="📊" title="No applicant data yet" />
          )}
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, marginBottom: '1.25rem', color: 'var(--color-text)' }}>
            Registered Users Distribution
          </h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={85}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 8,
                  color: 'var(--color-text)',
                  fontFamily: 'Plus Jakarta Sans',
                  boxShadow: 'var(--shadow-card)',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// ── 2. Indian Companies Management ──────────────────────────────
function CompanyManagement() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCompany, setSelectedCompany] = useState(null);

  const fetchCompanies = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/companies');
      setCompanies(data.companies || []);
    } catch {
      toast.error('Could not fetch companies directory');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  const filtered = companies.filter((c) =>
    c.company_name.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Loader text="Loading companies and job openings..." />;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Corporate Recruiting Partners</h1>
          <p>Explore leading Indian tech companies, enterprise partners, and active campus openings</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            className="input"
            style={{ width: 260 }}
            placeholder="🔍 Search companies (e.g. TCS, Zoho)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Overview Stats */}
      <div className="card-grid card-grid-3" style={{ marginBottom: '1.75rem' }}>
        <StatCard icon="🏢" label="Total Companies" value={companies.length} />
        <StatCard
          icon="📋"
          label="Total Job Openings"
          value={companies.reduce((sum, c) => sum + c.total_jobs, 0)}
        />
        <StatCard
          icon="👥"
          label="Total Matches Evaluated"
          value={companies.reduce((sum, c) => sum + c.total_matches, 0)}
        />
      </div>

      {/* Companies Grid */}
      <div className="card-grid card-grid-3" style={{ marginBottom: '2rem' }}>
        {filtered.map((company) => {
          const isSelected = selectedCompany?.company_name === company.company_name;
          const initial = company.company_name.charAt(0).toUpperCase();

          return (
            <div
              key={company.company_name}
              className="company-card"
              style={{
                borderColor: isSelected ? 'var(--color-action)' : undefined,
                cursor: 'pointer',
              }}
              onClick={() => setSelectedCompany(isSelected ? null : company)}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div className="company-avatar">{initial}</div>
                  <div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--color-text)' }}>
                      {company.company_name}
                    </h3>
                    <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                      Enterprise Partner
                    </span>
                  </div>
                </div>
                <span className="fit-badge fit-high">
                  {company.total_jobs} {company.total_jobs === 1 ? 'Job' : 'Jobs'}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Openings</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--color-text)' }} className="tabular-score">
                    {company.total_jobs}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Talent Matches</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--color-action)' }} className="tabular-score">
                    {company.total_matches}
                  </div>
                </div>
              </div>

              <button
                className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-outline'}`}
                style={{ width: '100%', justifyContent: 'center' }}
              >
                {isSelected ? '▲ Hide Openings' : '▼ View Job Openings'}
              </button>
            </div>
          );
        })}
      </div>

      {/* Expanded Company Job Listings */}
      {selectedCompany && (
        <div className="card fade-in" style={{ border: '1px solid var(--color-action)', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div className="company-avatar">{selectedCompany.company_name.charAt(0)}</div>
              <div>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--color-text)' }}>
                  {selectedCompany.company_name} — Active Job Openings
                </h2>
                <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
                  Showing {selectedCompany.jobs.length} open campus placement listings
                </p>
              </div>
            </div>
            <button
              onClick={() => setSelectedCompany(null)}
              className="btn btn-outline btn-sm"
            >
              ✕ Close View
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {selectedCompany.jobs.map((job) => (
              <div
                key={job.id}
                style={{
                  background: 'var(--color-surface-subtle)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius)',
                  padding: '1.25rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <div>
                    <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-text)' }}>
                      {job.title}
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Position ID #{job.id}
                    </span>
                  </div>
                  <span className="fit-badge fit-high tabular-score">
                    {job.match_count} Candidate Matches
                  </span>
                </div>

                <div style={{ marginTop: '0.5rem' }}>
                  <SkillTags skills={job.skills_required} variant="neutral" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {filtered.length === 0 && (
        <EmptyState
          icon="🏢"
          title="No Companies Found"
          desc="No companies match your search criteria. Try a different keyword."
        />
      )}
    </div>
  );
}

// ── 3. Student Data Management ──────────────────────────────────
function StudentManagement() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [addForm, setAddForm] = useState({ name: '', email: '', department: '', cgpa: '', password: 'student123' });
  const [bulkText, setBulkText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchStudents = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/students');
      setStudents(data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  const handleAddSingle = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/admin/students', {
        name: addForm.name,
        email: addForm.email,
        department: addForm.department || null,
        cgpa: addForm.cgpa ? parseFloat(addForm.cgpa) : null,
        password: addForm.password,
      });
      toast.success('Student added successfully! 🎓');
      setAddForm({ name: '', email: '', department: '', cgpa: '', password: 'student123' });
      setShowAddForm(false);
      await fetchStudents();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add student');
    } finally {
      setSubmitting(false);
    }
  };

  const handleBulkAdd = async () => {
    if (!bulkText.trim()) {
      toast.error('Please enter student data');
      return;
    }
    setSubmitting(true);
    try {
      const lines = bulkText.trim().split('\n').filter(Boolean);
      const studentsData = lines.map((line) => {
        const parts = line.split(',').map((p) => p.trim());
        return {
          name: parts[0] || '',
          email: parts[1] || '',
          department: parts[2] || null,
          cgpa: parts[3] ? parseFloat(parts[3]) : null,
          password: parts[4] || 'student123',
        };
      });

      const { data } = await api.post('/admin/students/bulk', { students: studentsData });
      toast.success(`Added ${data.total_created} students${data.total_errors ? ` (${data.total_errors} errors)` : ''} 🎓`);
      setBulkText('');
      setShowBulkForm(false);
      await fetchStudents();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Bulk add failed');
    } finally {
      setSubmitting(false);
    }
  };

  const deleteStudent = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete student "${name}"?`)) return;
    try {
      await api.delete(`/admin/students/${id}`);
      setStudents((prev) => prev.filter((s) => s.id !== id));
      toast.success('Student deleted successfully');
    } catch {
      toast.error('Could not delete student');
    }
  };

  const handleSeed100 = async () => {
    setSubmitting(true);
    try {
      const { data } = await api.post('/admin/seed-candidates');
      toast.success(`${data.total_created} candidates seeded successfully! 🎓`);
      await fetchStudents();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to seed candidates');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !students.length) return <Loader text="Loading student directory..." />;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Student Data Management</h1>
          <p>{students.length} registered students in placement database</p>
        </div>
        <button
          className="btn btn-primary btn-sm"
          onClick={handleSeed100}
          disabled={submitting}
          title="Seed 100 realistic default candidates across 10 technical profiles"
        >
          {submitting ? 'Seeding Candidates...' : '🌱 Seed 100 Default Candidates'}
        </button>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button
          className={`btn btn-sm ${showAddForm ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => { setShowAddForm(!showAddForm); setShowBulkForm(false); }}
        >
          ➕ Add Single Student
        </button>
        <button
          className={`btn btn-sm ${showBulkForm ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => { setShowBulkForm(!showBulkForm); setShowAddForm(false); }}
        >
          📋 Bulk Add Students
        </button>
      </div>

      {showAddForm && (
        <div className="card fade-in" style={{ marginBottom: '1.5rem', maxWidth: 640 }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--color-text)' }}>Add New Student</h3>
          <form onSubmit={handleAddSingle}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              <div className="form-group">
                <label className="form-label">Full Name *</label>
                <input
                  className="input"
                  value={addForm.name}
                  onChange={(e) => setAddForm({ ...addForm, name: e.target.value })}
                  placeholder="e.g. Ravi Kumar"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Email Address *</label>
                <input
                  className="input"
                  type="email"
                  value={addForm.email}
                  onChange={(e) => setAddForm({ ...addForm, email: e.target.value })}
                  placeholder="e.g. ravi@college.edu"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Department</label>
                <input
                  className="input"
                  value={addForm.department}
                  onChange={(e) => setAddForm({ ...addForm, department: e.target.value })}
                  placeholder="e.g. Computer Science"
                />
              </div>
              <div className="form-group">
                <label className="form-label">CGPA</label>
                <input
                  className="input"
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  value={addForm.cgpa}
                  onChange={(e) => setAddForm({ ...addForm, cgpa: e.target.value })}
                  placeholder="e.g. 8.5"
                />
              </div>
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
              style={{ marginTop: '0.5rem', width: '100%', justifyContent: 'center' }}
            >
              {submitting ? 'Adding Student...' : 'Add Student →'}
            </button>
          </form>
        </div>
      )}

      {showBulkForm && (
        <div className="card fade-in" style={{ marginBottom: '1.5rem', maxWidth: 700 }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--color-text)' }}>Bulk Add Students</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
            Enter one student per line in CSV format: <code>Name, Email, Department, CGPA</code>
          </p>
          <textarea
            className="textarea"
            rows={7}
            value={bulkText}
            onChange={(e) => setBulkText(e.target.value)}
            placeholder={`Ravi Kumar, ravi@college.edu, CSE, 8.5\nPriya Sharma, priya@college.edu, IT, 9.0`}
          />
          <button
            className="btn btn-primary"
            onClick={handleBulkAdd}
            disabled={submitting}
            style={{ marginTop: '1rem', width: '100%', justifyContent: 'center' }}
          >
            {submitting ? 'Adding Students...' : `Add Students →`}
          </button>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>CGPA</th>
              <th>Resume</th>
              <th>Skills</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {students.map((s) => (
              <tr key={s.id}>
                <td className="tabular-score" style={{ color: 'var(--text-muted)' }}>#{s.id}</td>
                <td style={{ fontWeight: 700, color: 'var(--color-text)' }}>{s.name}</td>
                <td style={{ color: 'var(--color-text-secondary)' }}>{s.email}</td>
                <td>{s.department || '—'}</td>
                <td className="tabular-score">{s.cgpa ?? '—'}</td>
                <td>
                  <span className={`fit-badge ${s.resume_path ? 'fit-high' : 'fit-low'}`}>
                    {s.resume_path ? '✓ Uploaded' : '✕ Missing'}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                    {s.skills?.length || 0} skills
                  </span>
                </td>
                <td>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => deleteStudent(s.id, s.name)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {students.length === 0 && <EmptyState icon="🎓" title="No students registered yet" />}
      </div>
    </div>
  );
}

// ── 4. User Directory ───────────────────────────────────────────
function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/users');
      setUsers(data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const deleteUser = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete user "${name}"?`)) return;
    try {
      await api.delete(`/admin/users/${id}`);
      setUsers((prev) => prev.filter((u) => u.id !== id));
      toast.success('User deleted successfully');
    } catch {
      toast.error('Could not delete user');
    }
  };

  if (loading && !users.length) return <Loader text="Loading user directory..." />;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>User Directory</h1>
          <p>{users.length} active platform accounts across all roles</p>
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td className="tabular-score" style={{ color: 'var(--text-muted)' }}>#{u.id}</td>
                <td style={{ fontWeight: 700, color: 'var(--color-text)' }}>{u.name}</td>
                <td style={{ color: 'var(--color-text-secondary)' }}>{u.email}</td>
                <td>
                  <span className="fit-badge fit-high" style={{ textTransform: 'uppercase' }}>
                    {u.role}
                  </span>
                </td>
                <td>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => deleteUser(u.id, u.name)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── 5. Reports ──────────────────────────────────────────────────
function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReports = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/reports');
      setReports(data.report || []);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  if (loading && !reports.length) return <Loader text="Generating placement readiness reports..." />;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>Placement Readiness Report</h1>
          <p>Institutional ranking and match suitability across campus candidates</p>
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Candidate Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>CGPA</th>
              <th>Top Match Score</th>
              <th>Shortlists</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r, i) => {
              const score = r.best_match_score;
              const { cls } = score !== null ? getFitTier(score) : { cls: '' };
              return (
                <tr key={i}>
                  <td style={{ fontWeight: 700, color: 'var(--color-text)' }}>{r.student_name}</td>
                  <td style={{ color: 'var(--color-text-secondary)' }}>{r.email}</td>
                  <td>{r.department || '—'}</td>
                  <td className="tabular-score">{r.cgpa ?? '—'}</td>
                  <td>
                    {score !== null ? (
                      <span className={`fit-badge ${cls} tabular-score`}>
                        {Math.round(score)}%
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>—</span>
                    )}
                  </td>
                  <td>
                    {r.shortlisted_count > 0 ? (
                      <span className="fit-badge fit-high tabular-score">
                        ★ {r.shortlisted_count} Shortlisted
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {reports.length === 0 && <EmptyState icon="📊" title="No report data available" />}
      </div>
    </div>
  );
}

// ── Root Admin Dashboard Layout ─────────────────────────────────
export default function AdminDashboardLayout() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/analytics');
      setAnalytics(data);
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const value = {
    analytics,
    loading,
    refreshAnalytics: fetchAnalytics,
  };

  return (
    <AdminContext.Provider value={value}>
      <div className="app-layout">
        <Sidebar links={NAV} />
        <div className="main-content">
          <Routes>
            <Route index element={<AdminHome />} />
            <Route path="companies" element={<CompanyManagement />} />
            <Route path="students"  element={<StudentManagement />} />
            <Route path="users"     element={<UserManagement />} />
            <Route path="reports"   element={<Reports />} />
            <Route path="*"         element={<Navigate to="/admin" replace />} />
          </Routes>
        </div>
      </div>
    </AdminContext.Provider>
  );
}
