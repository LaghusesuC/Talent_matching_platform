from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.core.security import require_role, hash_password
from app.models.user import User
from app.models.student import Student
from app.models.recruiter import Recruiter
from app.models.job import Job
from app.models.match import MatchResult, Shortlist
from app.schemas.auth import UserOut
from app.schemas.platform import StudentOut, StudentCreate, BulkStudentCreate

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserOut])
def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return db.query(User).all()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"message": "User not found"}
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted"}


@router.get("/analytics")
def get_analytics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    total_students = db.query(Student).count()
    total_recruiters = db.query(Recruiter).count()
    total_jobs = db.query(Job).count()
    total_matches = db.query(MatchResult).count()
    total_shortlists = db.query(Shortlist).count()

    avg_final_score = db.query(func.avg(MatchResult.final_score)).scalar() or 0
    avg_ats_score = db.query(func.avg(MatchResult.ats_score)).scalar() or 0

    top_jobs = (
        db.query(Job.title, func.count(MatchResult.id).label("applicants"))
        .join(MatchResult, MatchResult.job_id == Job.id)
        .group_by(Job.id)
        .order_by(func.count(MatchResult.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_students": total_students,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "total_matches": total_matches,
        "total_shortlists": total_shortlists,
        "avg_final_score": round(float(avg_final_score), 2),
        "avg_ats_score": round(float(avg_ats_score), 2),
        "top_jobs": [{"title": j.title, "applicants": j.applicants} for j in top_jobs],
    }


@router.get("/reports")
def generate_report(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    students = db.query(Student).all()
    report = []
    for s in students:
        best_match = (
            db.query(MatchResult)
            .filter(MatchResult.student_id == s.id)
            .order_by(MatchResult.final_score.desc())
            .first()
        )
        shortlisted_count = db.query(Shortlist).filter(Shortlist.student_id == s.id).count()
        report.append({
            "student_name": s.user.name,
            "email": s.user.email,
            "department": s.department,
            "cgpa": s.cgpa,
            "best_match_score": best_match.final_score if best_match else None,
            "shortlisted_count": shortlisted_count,
        })
    return {"report": report}


# ── Companies Endpoint ──────────────────────────────────────────

@router.get("/companies")
def list_companies(
    current_user: User = Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
):
    """List all companies with their job counts and top stats."""
    jobs = db.query(Job).all()
    company_map = {}
    for job in jobs:
        cname = job.company_name or "Unknown Company"
        if cname not in company_map:
            company_map[cname] = {
                "company_name": cname,
                "jobs": [],
                "total_jobs": 0,
                "total_matches": 0,
            }
        match_count = db.query(MatchResult).filter(MatchResult.job_id == job.id).count()
        company_map[cname]["jobs"].append({
            "id": job.id,
            "title": job.title,
            "skills_required": job.skills_required or [],
            "match_count": match_count,
            "created_at": str(job.created_at) if job.created_at else None,
        })
        company_map[cname]["total_jobs"] += 1
        company_map[cname]["total_matches"] += match_count

    companies = sorted(company_map.values(), key=lambda c: c["total_jobs"], reverse=True)
    return {"companies": companies, "total_companies": len(companies)}


# ── Student Data Management ─────────────────────────────────────

@router.get("/students", response_model=List[StudentOut])
def list_all_students(
    current_user: User = Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
):
    """List all students with their profile data."""
    students = db.query(Student).all()
    result = []
    for s in students:
        result.append(StudentOut(
            id=s.id,
            user_id=s.user_id,
            name=s.user.name,
            email=s.user.email,
            department=s.department,
            cgpa=s.cgpa,
            resume_path=s.resume_path,
            skills=(s.parsed_json or {}).get("skills", []),
        ))
    return result


@router.post("/students", response_model=StudentOut, status_code=201)
def add_student(
    data: StudentCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Add a single student (creates user account + student profile)."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail=f"Email '{data.email}' is already registered")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role="student",
    )
    db.add(user)
    db.flush()

    profile = Student(
        user_id=user.id,
        department=data.department,
        cgpa=data.cgpa,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return StudentOut(
        id=profile.id,
        user_id=user.id,
        name=user.name,
        email=user.email,
        department=profile.department,
        cgpa=profile.cgpa,
        resume_path=None,
        skills=[],
    )


@router.post("/students/bulk", status_code=201)
def add_students_bulk(
    data: BulkStudentCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Bulk-add multiple students at once."""
    created = []
    errors = []

    for idx, s in enumerate(data.students):
        if db.query(User).filter(User.email == s.email).first():
            errors.append({"index": idx, "email": s.email, "error": "Email already registered"})
            continue

        user = User(
            name=s.name,
            email=s.email,
            password_hash=hash_password(s.password),
            role="student",
        )
        db.add(user)
        db.flush()

        profile = Student(
            user_id=user.id,
            department=s.department,
            cgpa=s.cgpa,
        )
        db.add(profile)
        db.flush()

        created.append({
            "id": profile.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "department": profile.department,
            "cgpa": profile.cgpa,
        })

    db.commit()

    return {
        "message": f"Successfully added {len(created)} students",
        "created": created,
        "errors": errors,
        "total_created": len(created),
        "total_errors": len(errors),
    }


@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete a student and their associated user account."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    user = student.user
    db.query(MatchResult).filter(MatchResult.student_id == student_id).delete()
    db.query(Shortlist).filter(Shortlist.student_id == student_id).delete()
    db.delete(student)
    if user:
        db.delete(user)
    db.commit()

    return {"message": f"Student {student_id} deleted successfully"}


# ── Predefined Job Seeds (Indian Companies) ─────────────────────

PREDEFINED_JOBS = [
    # ── TCS (Tata Consultancy Services) ──
    {
        "company_name": "TCS",
        "title": "Full Stack Developer",
        "skills_required": ["React", "Node.js", "JavaScript", "PostgreSQL", "REST API", "Git", "HTML", "CSS"],
        "description": """TCS is hiring a Full Stack Developer for its Digital Engineering division.

Responsibilities:
- Design and develop scalable web applications using React and Node.js
- Build and maintain REST APIs and integrate third-party services
- Collaborate with designers and product managers to deliver high-quality features
- Write clean, testable, and well-documented code

Requirements:
- Proficiency in JavaScript/TypeScript, React, and Node.js
- Experience with relational databases (PostgreSQL, MySQL)
- Familiarity with RESTful API design and integration
- Knowledge of Git version control and CI/CD workflows

Keywords: React, Node.js, JavaScript, TypeScript, PostgreSQL, REST API, Git, HTML, CSS, Docker""",
    },
    {
        "company_name": "TCS",
        "title": "Data Scientist",
        "skills_required": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "Pandas", "SQL"],
        "description": """TCS Research & Innovation Lab seeks a Data Scientist to build intelligent AI solutions.

Responsibilities:
- Develop, train, and evaluate machine learning models for enterprise clients
- Process and analyze large datasets to extract actionable business insights
- Build end-to-end ML pipelines from data ingestion to model deployment
- Research and implement state-of-the-art algorithms for NLP and forecasting

Requirements:
- Strong Python programming skills
- Hands-on experience with TensorFlow or PyTorch
- Proficiency with Pandas, NumPy, Scikit-learn
- Understanding of statistical modeling and feature engineering

Keywords: Python, Machine Learning, Deep Learning, TensorFlow, Pandas, SQL, NLP, Data Science""",
    },
    # ── Infosys ──
    {
        "company_name": "Infosys",
        "title": "Cloud DevOps Engineer",
        "skills_required": ["Docker", "Kubernetes", "AWS", "Linux", "Git", "Python", "Terraform"],
        "description": """Infosys is looking for a Cloud DevOps Engineer to manage cloud infrastructure at scale.

Responsibilities:
- Design and maintain scalable cloud infrastructure on AWS and Azure
- Build and optimize CI/CD pipelines using Jenkins and GitHub Actions
- Manage containerized applications using Docker and Kubernetes
- Implement infrastructure-as-code using Terraform or CloudFormation

Requirements:
- Experience with AWS, GCP, or Azure cloud platforms
- Proficiency in Docker and Kubernetes orchestration
- Strong Linux/Unix administration skills
- Scripting in Bash and Python for automation

Keywords: Docker, Kubernetes, AWS, Azure, Linux, CI/CD, Terraform, DevOps, Python""",
    },
    {
        "company_name": "Infosys",
        "title": "Java Backend Developer",
        "skills_required": ["Java", "Spring Boot", "Microservices", "PostgreSQL", "Docker", "REST API", "Git"],
        "description": """Infosys BPM is hiring a Java Backend Developer for enterprise-grade solutions.

Responsibilities:
- Design and develop microservices using Java and Spring Boot
- Build scalable REST APIs and event-driven architectures
- Optimize database queries and manage PostgreSQL databases
- Deploy applications using Docker containers

Requirements:
- Strong Java programming skills (Java 11+)
- Experience with Spring Boot and Spring Cloud
- Knowledge of microservices architecture patterns
- Proficiency with PostgreSQL and Redis

Keywords: Java, Spring Boot, Microservices, PostgreSQL, Docker, REST API, Kafka""",
    },
    # ── Wipro ──
    {
        "company_name": "Wipro",
        "title": "React Frontend Engineer",
        "skills_required": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "REST API", "Git"],
        "description": """Wipro Digital is seeking a React Frontend Engineer for modern web application development.

Responsibilities:
- Build responsive, accessible web applications using React and TypeScript
- Implement pixel-perfect UI from Figma designs
- Optimize frontend performance and bundle sizes
- Write unit and integration tests with Jest and React Testing Library

Requirements:
- Strong React and TypeScript skills
- Proficiency in HTML5, CSS3, and responsive design
- Experience with state management (Redux, Zustand)
- Understanding of web accessibility (WCAG 2.1)

Keywords: React, TypeScript, JavaScript, HTML, CSS, Figma, Redux, Frontend""",
    },
    {
        "company_name": "Wipro",
        "title": "Cybersecurity Analyst",
        "skills_required": ["Linux", "Python", "Networking", "SIEM", "Penetration Testing"],
        "description": """Wipro CyberDefense Center is hiring a Cybersecurity Analyst to protect enterprise systems.

Responsibilities:
- Monitor security events and alerts using SIEM tools (Splunk, QRadar)
- Conduct vulnerability assessments and penetration testing
- Investigate security incidents and coordinate response
- Implement security controls: firewalls, IDS/IPS, DLP

Requirements:
- Knowledge of networking protocols (TCP/IP, DNS, HTTP/S, TLS)
- Familiarity with SIEM tools, IDS/IPS systems
- Scripting skills in Python or Bash
- CEH or OSCP certification preferred

Keywords: Cybersecurity, Linux, Python, SIEM, Penetration Testing, Firewall, Networking""",
    },
    # ── HCL Technologies ──
    {
        "company_name": "HCL Technologies",
        "title": "SAP ABAP Consultant",
        "skills_required": ["SAP", "ABAP", "SQL", "Communication", "ERP"],
        "description": """HCL Technologies is hiring an SAP ABAP Consultant for ERP implementation projects.

Responsibilities:
- Develop and customize SAP modules using ABAP programming
- Create technical specifications from functional requirements
- Perform unit testing and support user acceptance testing
- Provide production support and troubleshooting

Requirements:
- Strong SAP ABAP programming skills
- Experience with SAP S/4HANA or ECC
- Knowledge of SAP Fiori and OData services
- Good communication and client-facing skills

Keywords: SAP, ABAP, S/4HANA, Fiori, OData, ERP, SQL""",
    },
    {
        "company_name": "HCL Technologies",
        "title": "Python Automation Engineer",
        "skills_required": ["Python", "Selenium", "REST API", "SQL", "Git", "Jenkins"],
        "description": """HCL Technologies seeks a Python Automation Engineer for QA automation.

Responsibilities:
- Design and develop automated test frameworks using Python and Selenium
- Write API tests for RESTful services using requests/pytest
- Integrate automated tests into CI/CD pipelines with Jenkins
- Perform performance testing and generate test reports

Requirements:
- Strong Python programming skills
- Experience with Selenium WebDriver and pytest
- Knowledge of REST API testing
- Familiarity with CI/CD tools (Jenkins, GitHub Actions)

Keywords: Python, Selenium, Automation, REST API, SQL, Jenkins, pytest, QA""",
    },
    # ── Zoho ──
    {
        "company_name": "Zoho",
        "title": "Product Engineer - SaaS",
        "skills_required": ["Java", "JavaScript", "React", "MySQL", "REST API", "Git"],
        "description": """Zoho Corporation is looking for a Product Engineer to build world-class SaaS products.

Responsibilities:
- Design and develop features for Zoho's cloud-based business applications
- Build full-stack solutions using Java backend and React frontend
- Optimize application performance for millions of users
- Participate in product design discussions and code reviews

Requirements:
- Strong programming skills in Java and JavaScript
- Experience with React or Angular for frontend development
- Proficiency with MySQL and database optimization
- Passion for building products that solve real business problems

Keywords: Java, JavaScript, React, MySQL, SaaS, Product Engineering, REST API""",
    },
    {
        "company_name": "Zoho",
        "title": "Mobile App Developer",
        "skills_required": ["Java", "Kotlin", "Android", "REST API", "Firebase", "Git"],
        "description": """Zoho is hiring a Mobile App Developer for Android-based business applications.

Responsibilities:
- Develop and maintain Android applications using Kotlin and Java
- Design clean UI following Material Design guidelines
- Integrate REST APIs and third-party SDKs (Firebase)
- Publish and maintain apps on Google Play Store

Requirements:
- Proficiency in Kotlin and/or Java for Android
- Experience with Android SDK, Jetpack, and Room database
- Knowledge of REST API integration with Retrofit/OkHttp
- Familiarity with Firebase services

Keywords: Android, Kotlin, Java, Firebase, REST API, Jetpack, Material Design""",
    },
    # ── Cognizant ──
    {
        "company_name": "Cognizant",
        "title": "AI/ML Engineer",
        "skills_required": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "NLP", "Docker"],
        "description": """Cognizant Technology Solutions is hiring an AI/ML Engineer for its AI Practice.

Responsibilities:
- Build and deploy production-grade ML models for enterprise clients
- Develop NLP pipelines for text classification and entity extraction
- Fine-tune large language models for domain-specific applications
- Containerize ML services with Docker and deploy on cloud platforms

Requirements:
- Strong Python and ML framework skills (PyTorch, TensorFlow)
- Experience with NLP techniques and transformer models
- Knowledge of MLOps: MLflow, Docker, Kubernetes
- Understanding of distributed training and GPU optimization

Keywords: Python, Machine Learning, Deep Learning, PyTorch, NLP, Docker, MLOps, AI""",
    },
    {
        "company_name": "Cognizant",
        "title": "Business Analyst",
        "skills_required": ["Communication", "Leadership", "Agile", "Scrum", "SQL", "Jira"],
        "description": """Cognizant is hiring a Business Analyst for digital transformation projects.

Responsibilities:
- Gather and document business requirements from stakeholders
- Create product backlogs, user stories, and acceptance criteria
- Facilitate Agile ceremonies: sprint planning, standups, retrospectives
- Track KPIs and product metrics to inform roadmap decisions

Requirements:
- Excellent communication and stakeholder management skills
- Understanding of Agile/Scrum methodologies
- Basic SQL proficiency for data analysis and reporting
- Experience with Jira and Confluence

Keywords: Business Analysis, Agile, Scrum, SQL, Communication, Jira, Requirements""",
    },
    # ── Tech Mahindra ──
    {
        "company_name": "Tech Mahindra",
        "title": "Network Engineer",
        "skills_required": ["Networking", "Linux", "Cisco", "Python", "TCP/IP", "Firewall"],
        "description": """Tech Mahindra is seeking a Network Engineer for its telecom infrastructure division.

Responsibilities:
- Design and implement enterprise network architectures
- Configure and manage Cisco routers, switches, and firewalls
- Monitor network performance and troubleshoot connectivity issues
- Automate network configuration using Python and Ansible

Requirements:
- Strong knowledge of TCP/IP, DNS, DHCP, VPN
- Experience with Cisco networking equipment
- CCNA or CCNP certification preferred
- Scripting skills in Python for network automation

Keywords: Networking, Cisco, Linux, Python, TCP/IP, Firewall, CCNA, Ansible""",
    },
    {
        "company_name": "Tech Mahindra",
        "title": "Angular Frontend Developer",
        "skills_required": ["Angular", "TypeScript", "JavaScript", "HTML", "CSS", "REST API", "Git"],
        "description": """Tech Mahindra is looking for an Angular Frontend Developer for enterprise apps.

Responsibilities:
- Build enterprise web applications using Angular and TypeScript
- Develop reusable components and modules
- Integrate with backend REST APIs and GraphQL services
- Ensure cross-browser compatibility and responsive design

Requirements:
- Strong Angular (12+) and TypeScript skills
- Proficiency in HTML5 and CSS3/SCSS
- Experience with RxJS and NgRx state management
- Understanding of web performance optimization

Keywords: Angular, TypeScript, JavaScript, HTML, CSS, RxJS, NgRx, Frontend""",
    },
    # ── LTIMindtree ──
    {
        "company_name": "LTIMindtree",
        "title": "Cloud Data Engineer",
        "skills_required": ["Python", "SQL", "AWS", "Spark", "Kafka", "Hadoop", "Docker"],
        "description": """LTIMindtree is hiring a Cloud Data Engineer for its Data & Analytics practice.

Responsibilities:
- Build and maintain data pipelines using Apache Spark and Kafka
- Design data lake architectures on AWS (S3, Glue, Redshift)
- Optimize SQL queries and ETL processes for large-scale data
- Implement data quality checks and monitoring dashboards

Requirements:
- Strong Python and SQL skills
- Experience with Apache Spark, Kafka, and Hadoop ecosystem
- Knowledge of AWS data services (S3, Glue, Redshift, EMR)
- Familiarity with Docker and container orchestration

Keywords: Python, SQL, AWS, Spark, Kafka, Hadoop, Data Engineering, Docker""",
    },
    # ── Freshworks ──
    {
        "company_name": "Freshworks",
        "title": "Backend Engineer - Ruby on Rails",
        "skills_required": ["Ruby", "Rails", "PostgreSQL", "Redis", "REST API", "Docker", "Git"],
        "description": """Freshworks is seeking a Backend Engineer to build scalable SaaS products.

Responsibilities:
- Design and implement APIs and microservices using Ruby on Rails
- Architect and maintain PostgreSQL databases with optimal indexing
- Implement caching strategies with Redis and Sidekiq background jobs
- Write comprehensive tests and participate in code reviews

Requirements:
- Strong Ruby programming fundamentals
- Experience with Ruby on Rails web framework
- Proficiency with PostgreSQL and Redis
- Knowledge of RESTful API design patterns

Keywords: Ruby, Rails, PostgreSQL, Redis, Docker, REST API, Microservices, SaaS""",
    },
    {
        "company_name": "Freshworks",
        "title": "UI/UX Designer",
        "skills_required": ["Figma", "HTML", "CSS", "JavaScript", "React", "Git"],
        "description": """Freshworks is looking for a UI/UX Designer with frontend development skills.

Responsibilities:
- Design wireframes, prototypes, and high-fidelity mockups using Figma
- Conduct user research, usability testing, and A/B tests
- Translate designs into responsive frontend code (React/HTML/CSS)
- Maintain and evolve the design system and component library

Requirements:
- Proficiency in Figma for design and prototyping
- Strong HTML5, CSS3, and JavaScript skills
- Experience building React components
- Understanding of responsive design and accessibility

Keywords: Figma, UI, UX, React, HTML, CSS, JavaScript, Design System, Prototyping""",
    },
    # ── Razorpay ──
    {
        "company_name": "Razorpay",
        "title": "Backend Engineer - Go",
        "skills_required": ["Go", "PostgreSQL", "Redis", "Docker", "Kubernetes", "REST API", "Git"],
        "description": """Razorpay is hiring a Backend Engineer to build high-throughput payment systems.

Responsibilities:
- Design and develop low-latency payment APIs using Go
- Build distributed systems handling millions of transactions
- Implement database sharding and caching strategies
- Ensure PCI-DSS compliance in all payment processing

Requirements:
- Strong Go programming skills
- Experience with PostgreSQL and Redis
- Knowledge of distributed systems and message queues
- Familiarity with Docker and Kubernetes

Keywords: Go, Golang, PostgreSQL, Redis, Docker, Kubernetes, Payments, Fintech""",
    },
    # ── Flipkart ──
    {
        "company_name": "Flipkart",
        "title": "Software Development Engineer",
        "skills_required": ["Java", "Spring Boot", "Microservices", "MySQL", "Redis", "Kafka", "Docker"],
        "description": """Flipkart is looking for a Software Development Engineer for its e-commerce platform.

Responsibilities:
- Build and scale microservices handling millions of daily orders
- Design event-driven architectures using Kafka and RabbitMQ
- Optimize database performance for high-traffic scenarios
- Implement A/B testing frameworks and feature flags

Requirements:
- Strong Java and Spring Boot skills
- Experience with microservices architecture at scale
- Proficiency with MySQL, Redis, and Kafka
- Knowledge of distributed systems and caching

Keywords: Java, Spring Boot, Microservices, MySQL, Redis, Kafka, E-commerce, Docker""",
    },
    # ── Swiggy ──
    {
        "company_name": "Swiggy",
        "title": "ML Engineer - Recommendations",
        "skills_required": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "SQL", "Docker"],
        "description": """Swiggy is hiring an ML Engineer to build personalized recommendation systems.

Responsibilities:
- Build recommendation engines for food discovery and personalization
- Develop real-time ML scoring pipelines for restaurant ranking
- Train and evaluate deep learning models for user behavior prediction
- Collaborate with product teams to A/B test ML features

Requirements:
- Strong Python and ML skills (TensorFlow, PyTorch)
- Experience with recommendation systems and ranking algorithms
- Knowledge of feature stores and real-time serving
- Proficiency with SQL for data analysis

Keywords: Python, Machine Learning, Deep Learning, Recommendations, TensorFlow, SQL""",
    },
    # ── Zerodha ──
    {
        "company_name": "Zerodha",
        "title": "Full Stack Developer - Fintech",
        "skills_required": ["Python", "Go", "React", "PostgreSQL", "Redis", "Docker", "Git"],
        "description": """Zerodha is seeking a Full Stack Developer for its trading platform.

Responsibilities:
- Build high-performance trading interfaces using React
- Develop backend services in Python and Go for real-time data processing
- Design and maintain PostgreSQL databases for financial data
- Implement WebSocket-based real-time data streaming

Requirements:
- Strong Python/Go and React skills
- Experience with real-time systems and WebSockets
- Proficiency with PostgreSQL and Redis
- Understanding of financial markets (preferred)

Keywords: Python, Go, React, PostgreSQL, Redis, WebSocket, Fintech, Trading""",
    },
    # ── Juspay ──
    {
        "company_name": "Juspay",
        "title": "Haskell Functional Programmer",
        "skills_required": ["Haskell", "Functional Programming", "PostgreSQL", "Docker", "Git"],
        "description": """Juspay is hiring a Haskell Functional Programmer for payment orchestration systems.

Responsibilities:
- Build reliable payment orchestration services in Haskell
- Design type-safe APIs and domain-specific languages
- Implement high-availability distributed systems
- Write comprehensive property-based tests with QuickCheck

Requirements:
- Strong Haskell programming skills
- Understanding of functional programming patterns
- Experience with PostgreSQL and database design
- Knowledge of distributed systems concepts

Keywords: Haskell, Functional Programming, PostgreSQL, Docker, Payments, Distributed Systems""",
    },
    # ── Mphasis ──
    {
        "company_name": "Mphasis",
        "title": "ServiceNow Developer",
        "skills_required": ["ServiceNow", "JavaScript", "REST API", "SQL", "ITSM"],
        "description": """Mphasis is hiring a ServiceNow Developer for IT service management solutions.

Responsibilities:
- Develop and customize ServiceNow applications and workflows
- Create service catalog items, business rules, and UI policies
- Build integrations with external systems using REST APIs
- Provide support for ITSM, ITOM, and CSM modules

Requirements:
- ServiceNow Certified System Administrator (CSA)
- Strong JavaScript skills for ServiceNow scripting
- Experience with REST API integrations
- Knowledge of ITIL processes and ITSM workflows

Keywords: ServiceNow, JavaScript, REST API, ITSM, ITIL, SQL, Workflow Automation""",
    },
    # ── Persistent Systems ──
    {
        "company_name": "Persistent Systems",
        "title": "Embedded Systems Engineer",
        "skills_required": ["C", "C++", "Embedded Systems", "RTOS", "Linux", "Git"],
        "description": """Persistent Systems is hiring an Embedded Systems Engineer for IoT products.

Responsibilities:
- Develop firmware for embedded systems using C and C++
- Write device drivers and board support packages
- Implement communication protocols (I2C, SPI, UART, CAN)
- Debug and optimize embedded code using oscilloscopes and logic analyzers

Requirements:
- Strong C and C++ programming skills
- Experience with RTOS (FreeRTOS, Zephyr)
- Knowledge of embedded communication protocols
- Familiarity with ARM Cortex-M processors

Keywords: C, C++, Embedded Systems, RTOS, FreeRTOS, ARM, IoT, Linux""",
    },
    # ── Paytm ──
    {
        "company_name": "Paytm",
        "title": "Android Developer - Payments",
        "skills_required": ["Kotlin", "Java", "Android", "REST API", "Firebase", "Git"],
        "description": """Paytm is hiring an Android Developer for its mobile payments platform.

Responsibilities:
- Develop and maintain the Paytm Android app using Kotlin
- Implement UPI payment flows and wallet features
- Optimize app performance for low-end devices
- Integrate biometric authentication and security features

Requirements:
- Strong Kotlin and Java skills for Android development
- Experience with Android Jetpack and MVVM architecture
- Knowledge of payment SDK integrations
- Understanding of mobile security best practices

Keywords: Kotlin, Java, Android, Payments, UPI, Firebase, Jetpack, Mobile""",
    },
]


@router.post("/seed-jobs", status_code=201)
def seed_predefined_jobs(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Seed the database with predefined campus placement job listings from Indian companies.
    Creates recruiter accounts for each company if they don't exist.
    Skips jobs that already exist by title + company_name combination.
    """
    created_titles = []
    skipped_titles = []

    for job_data in PREDEFINED_JOBS:
        company = job_data["company_name"]
        title = job_data["title"]

        # Check if a job with this title + company already exists
        exists = db.query(Job).filter(
            Job.title == title,
            Job.company_name == company,
        ).first()
        if exists:
            skipped_titles.append(f"{company} - {title}")
            continue

        # Find or create a recruiter for this company
        recruiter = (
            db.query(Recruiter)
            .filter(Recruiter.company_name == company)
            .first()
        )
        if not recruiter:
            # Create a recruiter user for this company
            email_slug = company.lower().replace(" ", "").replace("&", "")[:12]
            rec_email = f"hr@{email_slug}.com"
            rec_user = db.query(User).filter(User.email == rec_email).first()
            if not rec_user:
                rec_user = User(
                    name=f"{company} HR",
                    email=rec_email,
                    password_hash=hash_password("recruiter123"),
                    role="recruiter",
                )
                db.add(rec_user)
                db.flush()

            recruiter = Recruiter(
                user_id=rec_user.id,
                company_name=company,
            )
            db.add(recruiter)
            db.flush()

        job = Job(
            recruiter_id=recruiter.id,
            title=title,
            company_name=company,
            description=job_data["description"],
            skills_required=job_data["skills_required"],
            parsed_json={
                "required_skills": job_data["skills_required"],
                "preferred_skills": [],
                "keywords": job_data["skills_required"],
            },
        )
        db.add(job)
        db.flush()

        # Compute match scores for all existing students with resumes
        from app.services.matcher import compute_match
        import app.services.embeddings as emb
        emb._model_failed = True
        students = db.query(Student).filter(Student.resume_text.isnot(None)).all()
        for student in students:
            resume_info = student.parsed_json or {}
            jd_info = job.parsed_json
            scores = compute_match(
                student.resume_text or "",
                job_data["description"],
                resume_info,
                jd_info,
                run_llm=False,
            )
            mr = MatchResult(
                student_id=student.id,
                job_id=job.id,
                rule_score=scores["rule_score"],
                semantic_score=scores["semantic_score"],
                llm_score=scores["llm_score"],
                final_score=scores["final_score"],
                matched_skills=scores["matched_skills"],
                missing_skills=scores["missing_skills"],
                explanation=scores["explanation"],
                ats_score=scores["ats_score"],
                improvement_suggestions=scores["improvement_suggestions"],
            )
            db.add(mr)

        created_titles.append(f"{company} - {title}")

    db.commit()

    return {
        "message": f"Seeded {len(created_titles)} predefined jobs from Indian companies",
        "created": created_titles,
        "skipped": skipped_titles,
        "total_created": len(created_titles),
        "total_skipped": len(skipped_titles),
    }


@router.post("/seed-candidates", status_code=201)
def seed_default_candidates(
    count: int = 100,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Seed the platform with up to 100 diverse default candidates with realistic
    skillsets, academic records, and projects, matched against existing jobs.
    """
    from app.services.seed_data import seed_candidates
    result = seed_candidates(db, target_count=min(max(count, 1), 100))
    return result
