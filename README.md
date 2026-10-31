# 🎯 TalentMatch AI — Campus Placement & AI Resume Screening Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

**TalentMatch AI** is a full-stack campus placement and recruitment screening platform that automatically parses student resumes, matches candidates against job descriptions using a hybrid AI scoring engine, and provides real-time recruitment analytics for placement officers and corporate recruiters.

---

## 🌟 Key Features

### 1. ⚡ High-Speed Resume Parsing (< 200ms)
- **Fast Text Extraction:** Uses **PyMuPDF (`fitz`)** as the primary high-speed extraction engine with automatic fallback to `pdfplumber` and `python-docx`.
- **MD5 Content Caching:** Resume and job description text hashes are cached in-memory to eliminate redundant LLM calls.
- **Competency Detection:** Instantly extracts contact information, GPA, department, technical skills, projects, and educational history.

### 2. 🧠 Hybrid 4-Tier Matching Engine
- **Rule-Based Overlap (40%):** Set-based exact skill intersection comparing candidate competencies against job criteria.
- **Semantic Vector Similarity (35%):** Local cosine similarity via **Sentence-Transformers** (`all-MiniLM-L6-v2`) vector embeddings with zero-network fallback.
- **ATS Keyword Matching (25%):** ATS keyword density check computing coverage across essential role keywords.
- **Deep Gemini LLM Analysis (On-Demand):** Uses **Google Gemini Flash** for qualitative candidate assessment, missing skill identification, and actionable resume improvement tips.

### 3. 🏢 Indian Corporate Partner Directory & Predefined Openings
- **Preconfigured Job Listings:** 28+ pre-seeded positions from India's leading tech employers:
  - **IT Services & Consulting:** TCS, Infosys, Wipro, HCL Technologies, Cognizant, Tech Mahindra, LTIMindtree, Mphasis.
  - **SaaS & Product:** Zoho, Freshworks, Persistent Systems.
  - **Fintech & Consumer Tech:** Razorpay, Flipkart, Swiggy, Zerodha, Juspay, Paytm.
- **Corporate Analytics:** Drill-down view of open positions, talent pool overlap, and applicant rankings per company.

### 4. 🎓 Comprehensive Student Data Management
- **Single & Bulk CSV Upload:** Placement cells can enroll individual students or bulk-import hundreds of students via CSV format (`Name, Email, Department, CGPA`).
- **100 Diverse Pre-Seeded Candidates:** Includes 100 realistic candidate profiles spanning Full Stack, Data Science, DevOps, Mobile, Cybersecurity, UI/UX, Cloud, Embedded, and Business Analysis.

### 5. 🎨 Multi-Theme UI System with Live Switcher
- **Modern Clean Light Theme (Default):** Crisp white cards, refined slate borders (`#E2E8F0`), and electric indigo/violet brand accents inspired by Stripe and Linear.
- **Midnight Dark Theme:** Deep obsidian navy (`#0A0F1D`) for low-light environments.
- **Cyber Emerald Theme:** High-tech matrix emerald palette (`#060D12`).
- **One-Click Switcher:** Persistent toggle in the sidebar with instant zero-flash switching.

### 6. ❓ Automated Interview Question Generator
- Generates 5 tailored, technical, and behavioral interview questions per candidate based on specific gaps between their resume and the target role.

---

## 🏗️ Architecture

```
resume-screening-platform/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Settings, environment configuration
│   │   │   └── security.py           # Bcrypt password hashing & JWT tokens
│   │   ├── models/
│   │   │   ├── user.py               # User table (Student, Recruiter, Admin)
│   │   │   ├── student.py            # Academic details & parsed resume JSON
│   │   │   ├── recruiter.py          # Corporate recruiter & company metadata
│   │   │   ├── job.py                # Job openings, company names & requirements
│   │   │   └── match.py              # Match scores, ATS ratings & shortlists
│   │   ├── routers/
│   │   │   ├── auth.py               # Authentication & registration endpoints
│   │   │   ├── students.py           # Resume uploads, matches & profile views
│   │   │   ├── jobs.py               # Job CRUD, candidate ranking & shortlisting
│   │   │   ├── candidates.py         # Tailored interview question generation
│   │   │   └── admin.py              # Companies, students, users & placement reports
│   │   ├── schemas/
│   │   │   ├── auth.py               # Authentication schemas
│   │   │   └── platform.py           # Job, Candidate, Match, and Student schemas
│   │   ├── services/
│   │   │   ├── parser.py             # Fast PyMuPDF & docx text extraction
│   │   │   ├── matcher.py            # Hybrid rule + semantic + ATS scoring
│   │   │   ├── embeddings.py         # Sentence-Transformers vector similarity
│   │   │   ├── llm.py                # Gemini AI candidate screening & ATS engine
│   │   │   └── seed_data.py          # 100 realistic student candidate profiles
│   │   ├── database.py               # SQLAlchemy database session setup
│   │   └── main.py                   # FastAPI application initialization & CORS
│   ├── requirements.txt              # Backend dependencies
│   ├── run_backend.bat               # Windows 1-click backend runner
│   ├── seed_indian_jobs.py           # Standalone seed script for Indian company jobs
│   └── .env.example                  # Environment configuration template
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js             # Axios client with JWT interceptor & proxying
│   │   ├── components/
│   │   │   ├── Sidebar.jsx           # Modern navigation with live Theme Switcher
│   │   │   └── UI.jsx                # FitBar, CandidateRow, StatCard, SkillTags
│   │   ├── context/
│   │   │   └── AuthContext.jsx       # Authentication state & role routing
│   │   ├── pages/
│   │   │   ├── AuthPage.jsx          # Login & registration with role selector
│   │   │   ├── StudentDashboard.jsx  # Student hub, resume upload & job matches
│   │   │   ├── RecruiterDashboard.jsx# Job management & candidate screening
│   │   │   └── AdminDashboard.jsx    # Institutional analytics & company management
│   │   ├── App.jsx                   # Application routes & toast notifications
│   │   ├── main.jsx                  # React bootstrap
│   │   └── index.css                 # Multi-theme design tokens & layouts
│   ├── package.json
│   ├── vite.config.js                # Vite configuration with tunnel & reverse proxy
│   └── run_frontend.bat              # Windows 1-click frontend runner
│
├── start_tunnel.bat                  # 1-click public web tunnel runner
├── .gitignore                        # Complete repository exclusions
└── README.md                         # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python:** 3.10 or 3.11 recommended
- **Node.js:** 18+ (Node 20+ or 24+ supported)
- **npm:** 9+

---

### 2. Backend Setup

```powershell
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env
# (Optional) Add your Google Gemini API key to .env for AI-augmented insights

# 5. Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> **Windows Tip:** You can also simply double-click [`backend/run_backend.bat`](file:///e:/Project/resume-screening-platform/backend/run_backend.bat) to launch the backend automatically.

- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 3. Frontend Setup

```powershell
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

> **Windows Tip:** You can also double-click [`frontend/run_frontend.bat`](file:///e:/Project/resume-screening-platform/frontend/run_frontend.bat).

- **Web Application:** [http://localhost:5173](http://localhost:5173)

---

### 4. Public Web Tunneling (Optional)

If you wish to test on a mobile device or share a live link with someone outside your local network without port-forwarding issues:

Double-click [`start_tunnel.bat`](file:///e:/Project/resume-screening-platform/start_tunnel.bat) or run:
```powershell
npx localtunnel --port 5173
```
*Note: Vite is already configured with `allowedHosts: true` and built-in API proxying, so public tunnel URLs will work with zero configuration.*

---

## 🔑 Demo Accounts

Use any of these pre-configured accounts to explore the role-specific dashboards:

| Role | Email | Password | Access Highlights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@test.com` | `password123` | Placement Analytics, Company Directory, Bulk Student Management, Reports |
| **Recruiter** | `recruiter@test.com` | `password123` | Post Jobs, Candidate Rankings, Fit Breakdown, Interview Questions |
| **Student** | `student@test.com` | `password123` | Resume Upload, Extracted Skills, Ranked Job Matches, Improvement Tips |

*(You can also create a new account anytime via the **Create Account** tab on the login screen).*

---

## 🛠️ Seeding Initial Data

To populate the database with realistic sample data:
1. Log in as **Admin** (`admin@test.com` / `password123`).
2. Go to **Dashboard** and click **🌱 Seed Indian Company Jobs** (seeds 25+ openings from TCS, Infosys, Zoho, Cognizant, etc.).
3. Go to **Students** and click **🌱 Seed 100 Default Candidates** (seeds 100 students across 10 skill profiles with matching results).

Alternatively, run the seeding scripts directly from the terminal:
```powershell
cd backend
python seed_indian_jobs.py
```

---

## 📡 API Endpoints Overview

### Authentication (`/auth`)
- `POST /auth/register` — Register a student or corporate recruiter
- `POST /auth/login` — Authenticate and receive a JWT Bearer token
- `GET /auth/me` — Retrieve the authenticated user profile

### Students (`/students`)
- `POST /students/resume` — Upload and parse resume (PDF, DOCX, TXT) with performance metrics
- `GET /students/me` — Get student academic details and extracted skills
- `GET /students/me/matches` — Get all corporate jobs ranked by AI compatibility score
- `GET /students/me/suggestions/{job_id}` — Get ATS keyword coverage and resume improvement tips

### Jobs & Screening (`/jobs`)
- `GET /jobs` — List all active job postings
- `POST /jobs` — Create a new job listing with required skills
- `GET /jobs/{id}/candidates` — Screen and rank registered students against a job
- `POST /jobs/{id}/shortlist` — Shortlist or update candidate recruitment status

### Administration (`/admin`)
- `GET /admin/analytics` — High-level institutional placement statistics
- `GET /admin/companies` — Indian corporate partners, active openings, and match counts
- `GET /admin/students` — Student database directory
- `POST /admin/students` — Register an individual student
- `POST /admin/students/bulk` — Bulk enroll students via CSV
- `DELETE /admin/students/{id}` — Remove student and associated matching records
- `GET /admin/reports` — Placement readiness and shortlisted candidate report
- `POST /admin/seed-jobs` — Seed preconfigured Indian company jobs
- `POST /admin/seed-candidates` — Seed default technical candidate pool

---

## 🛡️ Security & Best Practices

- **Secure Environment Variables:** Secrets, API keys, and database files are excluded from Git via `.gitignore`. Use `.env.example` as a template.
- **Password Hashing:** Passwords are encrypted using salted **Bcrypt** hashes.
- **Stateless Authentication:** Protected routes verify **JWT Bearer tokens** signed with HMAC-SHA256.
- **Role-Based Access Control:** Role requirements (`admin`, `recruiter`, `student`) are strictly enforced on backend endpoints and frontend routes.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
