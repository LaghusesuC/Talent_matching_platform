"""
Seed Data Generator for 100 Default Candidates.
Generates diverse, realistic students with varied skillsets, academic backgrounds,
projects, and work experiences for campus placement screening.
"""
from app.core.security import hash_password
from app.models.user import User
from app.models.student import Student
from app.models.job import Job
from app.models.match import MatchResult
from app.services.matcher import compute_match

NAMES = [
    # Cluster 1: Full Stack Web Developers
    ("Aarav Sharma", "aarav.sharma@campus.edu", "CSE", 8.85),
    ("Ananya Iyer", "ananya.iyer@campus.edu", "IT", 9.12),
    ("Rohan Verma", "rohan.verma@campus.edu", "CSE", 7.95),
    ("Diya Patel", "diya.patel@campus.edu", "Information Technology", 8.40),
    ("Siddharth Rao", "siddharth.rao@campus.edu", "CSE", 8.70),
    ("Kavya Nair", "kavya.nair@campus.edu", "Software Engineering", 9.25),
    ("Aditya Joshi", "aditya.joshi@campus.edu", "CSE", 7.65),
    ("Meera Kulkarni", "meera.kulkarni@campus.edu", "IT", 8.90),
    ("Arjun Reddy", "arjun.reddy@campus.edu", "CSE", 8.30),
    ("Tanvi Deshmukh", "tanvi.deshmukh@campus.edu", "Information Technology", 9.05),

    # Cluster 2: Data Science & ML Engineers
    ("Vikram Malhotra", "vikram.malhotra@campus.edu", "AI & Data Science", 9.40),
    ("Pooja Sundaram", "pooja.sundaram@campus.edu", "Computer Science", 8.95),
    ("Rahul Nambiar", "rahul.nambiar@campus.edu", "AI & Data Science", 8.50),
    ("Sneha Chatterjee", "sneha.chatterjee@campus.edu", "Data Science", 9.15),
    ("Nikhil Gupta", "nikhil.gupta@campus.edu", "CSE", 8.20),
    ("Ishita Sengupta", "ishita.sengupta@campus.edu", "AI & Data Science", 9.35),
    ("Karthik Menon", "karthik.menon@campus.edu", "CSE", 7.80),
    ("Shreya Pillai", "shreya.pillai@campus.edu", "Data Analytics", 8.65),
    ("Varun Choudhary", "varun.choudhary@campus.edu", "AI & Data Science", 8.90),
    ("Riya Saxena", "riya.saxena@campus.edu", "CSE", 9.10),

    # Cluster 3: Backend & Cloud Engineers
    ("Harsh Vardhan", "harsh.vardhan@campus.edu", "CSE", 8.60),
    ("Anjali Mishra", "anjali.mishra@campus.edu", "IT", 8.45),
    ("Pranav Hegde", "pranav.hegde@campus.edu", "CSE", 9.20),
    ("Neha Bhat", "neha.bhat@campus.edu", "Software Engineering", 8.75),
    ("Devendra Singh", "devendra.singh@campus.edu", "CSE", 7.90),
    ("Swati Agarwal", "swati.agarwal@campus.edu", "IT", 8.80),
    ("Manish Tiwari", "manish.tiwari@campus.edu", "CSE", 8.15),
    ("Ritu Das", "ritu.das@campus.edu", "Information Technology", 8.95),
    ("Aman Kapoor", "aman.kapoor@campus.edu", "CSE", 8.35),
    ("Priya Venkatesh", "priya.venkatesh@campus.edu", "Software Engineering", 9.00),

    # Cluster 4: DevOps & Infrastructure Engineers
    ("Gautam Sethi", "gautam.sethi@campus.edu", "CSE", 8.55),
    ("Divya Namboodiri", "divya.namboodiri@campus.edu", "IT", 9.10),
    ("Kunal Mehra", "kunal.mehra@campus.edu", "CSE", 7.85),
    ("Sanya Mirza", "sanya.mirza@campus.edu", "ECE", 8.40),
    ("Yash Singhal", "yash.singhal@campus.edu", "CSE", 8.70),
    ("Simran Kaur", "simran.kaur@campus.edu", "IT", 8.95),
    ("Akshay Chawla", "akshay.chawla@campus.edu", "CSE", 8.25),
    ("Nandini Murthy", "nandini.murthy@campus.edu", "ECE", 8.60),
    ("Sameer Kaushik", "sameer.kaushik@campus.edu", "CSE", 9.05),
    ("Shruti Bose", "shruti.bose@campus.edu", "IT", 8.30),

    # Cluster 5: Mobile App Developers (Android/iOS/Flutter)
    ("Abhishek Pandey", "abhishek.pandey@campus.edu", "CSE", 8.40),
    ("Meghna Roy", "meghna.roy@campus.edu", "IT", 9.15),
    ("Tushar Mittal", "tushar.mittal@campus.edu", "CSE", 7.95),
    ("Sonali Ghosh", "sonali.ghosh@campus.edu", "ECE", 8.50),
    ("Rohit Soni", "rohit.soni@campus.edu", "CSE", 8.80),
    ("Bhavna Shah", "bhavna.shah@campus.edu", "IT", 8.70),
    ("Tarun Goyal", "tarun.goyal@campus.edu", "Software Engineering", 8.10),
    ("Pallavi Dixit", "pallavi.dixit@campus.edu", "CSE", 9.20),
    ("Mohit Bajaj", "mohit.bajaj@campus.edu", "IT", 8.35),
    ("Aayushi Jain", "aayushi.jain@campus.edu", "CSE", 8.90),

    # Cluster 6: Cybersecurity & Network Analysts
    ("Deepak Rawat", "deepak.rawat@campus.edu", "Information Security", 8.85),
    ("Kriti Sanon", "kriti.sanon@campus.edu", "CSE", 9.30),
    ("Vishal Chauhan", "vishal.chauhan@campus.edu", "IT", 7.75),
    ("Radhika Apte", "radhika.apte@campus.edu", "Cybersecurity", 9.00),
    ("Ayushmann Khurana", "ayushmann.khurana@campus.edu", "CSE", 8.45),
    ("Richa Chadha", "richa.chadha@campus.edu", "IT", 8.65),
    ("Rajkummar Rao", "rajkummar.rao@campus.edu", "Cybersecurity", 8.95),
    ("Fatima Sana", "fatima.sana@campus.edu", "CSE", 8.20),
    ("Vicky Kaushal", "vicky.kaushal@campus.edu", "Information Technology", 9.10),
    ("Sanya Malhotra", "sanya.malhotra@campus.edu", "CSE", 8.50),

    # Cluster 7: Frontend & UI/UX Engineers
    ("Naveen Polishetty", "naveen.polishetty@campus.edu", "CSE", 8.60),
    ("Rashmika Mandanna", "rashmika.mandanna@campus.edu", "Design & Tech", 9.25),
    ("Vijay Deverakonda", "vijay.deverakonda@campus.edu", "IT", 7.90),
    ("Samantha Ruth", "samantha.ruth@campus.edu", "CSE", 9.40),
    ("Dulquer Salmaan", "dulquer.salmaan@campus.edu", "Information Technology", 8.75),
    ("Sai Pallavi", "sai.pallavi@campus.edu", "CSE", 9.50),
    ("Nivin Pauly", "nivin.pauly@campus.edu", "IT", 8.15),
    ("Keerthy Suresh", "keerthy.suresh@campus.edu", "Design & Computing", 9.05),
    ("Tovino Thomas", "tovino.thomas@campus.edu", "CSE", 8.35),
    ("Parvathy Thiruvothu", "parvathy.thiruvothu@campus.edu", "IT", 8.90),

    # Cluster 8: Cloud & Big Data Engineers
    ("Alex Johnson", "alex.johnson@campus.edu", "Computer Science", 8.70),
    ("Emily Chen", "emily.chen@campus.edu", "Data Engineering", 9.35),
    ("Michael Brown", "michael.brown@campus.edu", "CSE", 8.10),
    ("Sarah Williams", "sarah.williams@campus.edu", "IT", 8.85),
    ("David Martinez", "david.martinez@campus.edu", "CSE", 8.45),
    ("Jessica Taylor", "jessica.taylor@campus.edu", "Data Science", 9.15),
    ("James Wilson", "james.wilson@campus.edu", "CSE", 7.80),
    ("Sophia Anderson", "sophia.anderson@campus.edu", "Computer Science", 9.00),
    ("Daniel Thomas", "daniel.thomas@campus.edu", "IT", 8.25),
    ("Olivia Jackson", "olivia.jackson@campus.edu", "Data Engineering", 9.20),

    # Cluster 9: Embedded Systems & IoT Engineers
    ("Lucas White", "lucas.white@campus.edu", "ECE", 8.90),
    ("Mia Harris", "mia.harris@campus.edu", "Electronics", 9.10),
    ("Ethan Martin", "ethan.martin@campus.edu", "EEE", 8.20),
    ("Ava Thompson", "ava.thompson@campus.edu", "ECE", 8.75),
    ("Noah Garcia", "noah.garcia@campus.edu", "Embedded Systems", 9.30),
    ("Isabella Martinez", "isabella.martinez@campus.edu", "ECE", 8.45),
    ("Liam Robinson", "liam.robinson@campus.edu", "EEE", 7.95),
    ("Charlotte Clark", "charlotte.clark@campus.edu", "ECE", 9.05),
    ("Mason Rodriguez", "mason.rodriguez@campus.edu", "Electronics", 8.60),
    ("Amelia Lewis", "amelia.lewis@campus.edu", "ECE", 8.80),

    # Cluster 10: Business Analysis & Product Tech
    ("Logan Lee", "logan.lee@campus.edu", "Management & Tech", 8.65),
    ("Harper Walker", "harper.walker@campus.edu", "Information Systems", 9.15),
    ("Benjamin Hall", "benjamin.hall@campus.edu", "CSE", 8.30),
    ("Evelyn Allen", "evelyn.allen@campus.edu", "Business Analytics", 8.95),
    ("Oliver Young", "oliver.young@campus.edu", "IT", 8.50),
    ("Abigail King", "abigail.king@campus.edu", "Management Studies", 9.00),
    ("Elijah Wright", "elijah.wright@campus.edu", "CSE", 7.85),
    ("Emily Scott", "emily.scott@campus.edu", "Information Systems", 8.70),
    ("Alexander Green", "alexander.green@campus.edu", "Business Analytics", 9.20),
    ("Elizabeth Adams", "elizabeth.adams@campus.edu", "IT", 8.40),
]

CLUSTER_TEMPLATES = [
    # 0: Full Stack Web Developer
    {
        "skills": ["React", "Node.js", "Express", "JavaScript", "TypeScript", "PostgreSQL", "MongoDB", "REST API", "Git", "HTML", "CSS", "Tailwind CSS"],
        "summary": "Motivated Full Stack Web Developer skilled in modern JavaScript/TypeScript, React frontends, and Node.js microservices. Proven ability to build responsive web applications with database persistence.",
        "projects": [
            {"name": "Campus Placement Portal", "description": "Built end-to-end portal using React, Node.js, Express, and PostgreSQL with JWT auth and real-time application tracking.", "technologies_used": ["React", "Node.js", "PostgreSQL", "REST API"]},
            {"name": "E-Commerce Microservices Platform", "description": "Architected product catalog and checkout service utilizing MongoDB, Express, and Docker containers.", "technologies_used": ["MongoDB", "Express", "Docker", "JavaScript"]},
        ],
        "experience": [
            {"company": "TechCorp Solutions", "role": "Full Stack Intern", "duration": "Jun 2024 - Aug 2024", "description": "Developed React dashboard components and integrated RESTful APIs reducing page load latency by 25%."}
        ],
        "certifications": ["Meta Full Stack Developer Certificate", "PostgreSQL Database Administration"],
    },
    # 1: Data Science & ML Engineer
    {
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "SQL", "Data Science", "NLP"],
        "summary": "Aspiring Data Scientist with deep foundations in Machine Learning, Statistical Modeling, and Python. Passionate about leveraging deep learning frameworks to solve complex pattern recognition problems.",
        "projects": [
            {"name": "Resume Intelligence & Ranking Engine", "description": "Created NLP matching algorithm using Python, Scikit-learn, and cosine similarity with 91% accuracy against human benchmarks.", "technologies_used": ["Python", "NLP", "Scikit-learn", "Pandas"]},
            {"name": "Medical Image Classification", "description": "Trained Convolutional Neural Networks using PyTorch on 50,000+ radiology images achieving 94.2% test accuracy.", "technologies_used": ["Python", "PyTorch", "Deep Learning", "NumPy"]},
        ],
        "experience": [
            {"company": "DataMinds AI Labs", "role": "Data Science Research Intern", "duration": "May 2024 - Jul 2024", "description": "Preprocessed multi-gigabyte tabular datasets using Pandas and fine-tuned XGBoost regression models."}
        ],
        "certifications": ["Deep Learning Specialization (Coursera)", "TensorFlow Developer Certificate"],
    },
    # 2: Backend Software Engineer
    {
        "skills": ["Python", "Django", "FastAPI", "Flask", "PostgreSQL", "Redis", "Docker", "REST API", "Git", "Linux", "Microservices"],
        "summary": "Backend Software Engineer focused on high-throughput REST APIs, asynchronous tasks, and scalable relational database designs using Python, FastAPI, and PostgreSQL.",
        "projects": [
            {"name": "Scalable Banking API Gateway", "description": "Constructed asynchronous REST API with FastAPI, Redis caching, and PostgreSQL handling 2,000 requests per second.", "technologies_used": ["FastAPI", "Python", "Redis", "PostgreSQL"]},
            {"name": "Distributed Task Scheduler", "description": "Built background worker system with Celery and Redis to process scheduled automated emails and report generation.", "technologies_used": ["Python", "Django", "Docker", "Git"]},
        ],
        "experience": [
            {"company": "Fintech Innovations", "role": "Backend Engineering Intern", "duration": "Jan 2024 - Jun 2024", "description": "Refactored legacy endpoints into async FastAPI routes, slashing response times from 320ms to 45ms."}
        ],
        "certifications": ["Docker Certified Associate", "AWS Certified Cloud Practitioner"],
    },
    # 3: DevOps & Cloud Infrastructure
    {
        "skills": ["Docker", "Kubernetes", "AWS", "Linux", "Git", "CI/CD", "Terraform", "Python", "Bash", "Prometheus", "Grafana"],
        "summary": "DevOps enthusiast with practical expertise in container orchestration, infrastructure as code, and automated CI/CD deployment pipelines on AWS and Linux environments.",
        "projects": [
            {"name": "Zero-Downtime Kubernetes Cluster", "description": "Deployed fault-tolerant microservices cluster on AWS EKS with Prometheus monitoring and Grafana alerting.", "technologies_used": ["Kubernetes", "AWS", "Docker", "Terraform"]},
            {"name": "Automated Multi-Stage CI/CD Pipeline", "description": "Built GitHub Actions workflow with automated unit testing, container vulnerability scanning, and Docker deployment.", "technologies_used": ["CI/CD", "Docker", "Linux", "Bash"]},
        ],
        "experience": [
            {"company": "CloudScale Systems", "role": "Cloud Operations Intern", "duration": "May 2024 - Aug 2024", "description": "Automated AWS infrastructure provisioning using Terraform scripts, reducing server spin-up time by 80%."}
        ],
        "certifications": ["AWS Certified Solutions Architect - Associate", "Certified Kubernetes Application Developer (CKAD)"],
    },
    # 4: Mobile Application Developer
    {
        "skills": ["Android", "Kotlin", "Java", "Flutter", "Firebase", "REST API", "Git", "SQL", "Material Design", "Jetpack"],
        "summary": "Creative Mobile App Developer specializing in native Android (Kotlin) and cross-platform Flutter applications with offline database synchronization and Firebase integrations.",
        "projects": [
            {"name": "Campus Event Navigator", "description": "Published native Android app with 3,000+ downloads featuring real-time maps, Firebase Auth, and SQLite caching.", "technologies_used": ["Kotlin", "Android", "Firebase", "Material Design"]},
            {"name": "Personal Finance Tracker", "description": "Built Flutter app with reactive state management, exportable PDF reports, and encrypted SQLite storage.", "technologies_used": ["Flutter", "Dart", "SQL", "Git"]},
        ],
        "experience": [
            {"company": "Appify Mobile Studio", "role": "Android Developer Intern", "duration": "May 2024 - Jul 2024", "description": "Migrated Java Activities to Kotlin Jetpack Compose components and integrated Retrofit REST API clients."}
        ],
        "certifications": ["Google Associate Android Developer", "Flutter Certified Professional"],
    },
    # 5: Cybersecurity Analyst
    {
        "skills": ["Cybersecurity", "Linux", "Python", "Networking", "SQL", "Git", "SIEM", "Penetration Testing", "Firewall", "Vulnerability Assessment"],
        "summary": "Security-focused analyst with strong grasp of network protocols, threat modeling, security log analysis, and automated vulnerability scanning using Python and Linux tools.",
        "projects": [
            {"name": "Network Intrusion Detection System", "description": "Configured Snort IDS and integrated ELK Stack to capture, parse, and alert on malicious port scanning activities.", "technologies_used": ["Linux", "Networking", "SIEM", "Python"]},
            {"name": "Automated Web Vulnerability Scanner", "description": "Created Python script identifying SQL injection and XSS vulnerabilities in test staging environments.", "technologies_used": ["Python", "SQL", "Git", "Penetration Testing"]},
        ],
        "experience": [
            {"company": "CyberShield Defense", "role": "Security Operations Intern", "duration": "Jun 2024 - Aug 2024", "description": "Monitored 1,000+ endpoint logs via SIEM dashboard, escalating 14 verified security events for rapid containment."}
        ],
        "certifications": ["CompTIA Security+", "Certified Ethical Hacker (CEH)"],
    },
    # 6: UI/UX Designer & Frontend Developer
    {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Figma", "Git", "UI", "UX", "Tailwind CSS", "Design System", "Accessibility"],
        "summary": "Detail-oriented frontend engineer and interface designer who bridges user research in Figma with pixel-perfect, accessible React and Tailwind CSS web applications.",
        "projects": [
            {"name": "Healthcare Telehealth Interface", "description": "Designed high-fidelity interactive Figma prototype and implemented WCAG 2.1 AA accessible React frontend.", "technologies_used": ["React", "Figma", "HTML", "CSS", "Accessibility"]},
            {"name": "Design System & Component Library", "description": "Crafted 40+ reusable UI components with Storybook, Tailwind CSS, and strict TypeScript typings.", "technologies_used": ["React", "JavaScript", "Tailwind CSS", "Git"]},
        ],
        "experience": [
            {"company": "PixelCraft Studios", "role": "UI/UX Design Intern", "duration": "Jan 2024 - May 2024", "description": "Conducted 18 usability test sessions and redesigned onboarding flows, increasing conversion rate by 34%."}
        ],
        "certifications": ["Google UX Design Professional Certificate", "Frontend Development with React (Meta)"],
    },
    # 7: Cloud Data Engineer & Big Data
    {
        "skills": ["Python", "Java", "SQL", "AWS", "Docker", "PostgreSQL", "Git", "Linux", "REST API", "Machine Learning"],
        "summary": "Data Engineer adept at designing reliable ETL pipelines, database schemas, and streaming architectures to transform raw enterprise data into analytical assets.",
        "projects": [
            {"name": "Real-time Clickstream Pipeline", "description": "Constructed streaming pipeline using Kafka, Python, and PostgreSQL processing 10,000 events/minute.", "technologies_used": ["Python", "SQL", "Docker", "PostgreSQL"]},
            {"name": "Automated Data Warehouse Ingestion", "description": "Orchestrated Airflow DAGs extracting data from REST APIs into AWS S3 and PostgreSQL analytical stores.", "technologies_used": ["AWS", "Python", "Git", "SQL"]},
        ],
        "experience": [
            {"company": "DataStream Analytics", "role": "Data Engineering Intern", "duration": "May 2024 - Aug 2024", "description": "Optimized complex SQL analytical queries, reducing daily ETL processing window from 4 hours to 45 minutes."}
        ],
        "certifications": ["AWS Certified Data Analytics", "Astronomer Certified Airflow Fundamentals"],
    },
    # 8: Embedded Systems & IoT Engineer
    {
        "skills": ["C++", "Python", "Linux", "Git", "REST API", "SQL", "Networking", "Machine Learning"],
        "summary": "Hardware-software systems engineer passionate about firmware, low-level programming in C++, embedded Linux, and smart sensor telemetry protocols.",
        "projects": [
            {"name": "Smart Campus Environmental Monitor", "description": "Engineered low-power sensor node collecting air quality metrics over MQTT to a centralized web dashboard.", "technologies_used": ["C++", "Python", "Networking", "Git"]},
            {"name": "Autonomous Line-Tracking Robot", "description": "Programmed PID control algorithms in C++ running on microcontroller with real-time obstacle avoidance.", "technologies_used": ["C++", "Linux", "Git"]},
        ],
        "experience": [
            {"company": "IoTronics Hardware Labs", "role": "Embedded Systems Intern", "duration": "May 2024 - Jul 2024", "description": "Wrote device drivers and debugged SPI and I2C peripheral communications on ARM Cortex boards."}
        ],
        "certifications": ["Embedded Systems Architecture (Arm)", "IoT Programming Fundamentals"],
    },
    # 9: Business Analyst & Product Manager
    {
        "skills": ["SQL", "Communication", "Leadership", "Agile", "Scrum", "Git", "Python", "Requirements", "Data Analysis"],
        "summary": "Analytical and communicative Business Analyst skilled at translating user needs into user stories, building interactive SQL dashboards, and steering agile sprint deliveries.",
        "projects": [
            {"name": "Customer Churn Predictive Analysis", "description": "Analyzed 100,000+ subscription records using SQL and Python to isolate key churn factors, presented to leadership.", "technologies_used": ["SQL", "Python", "Data Analysis", "Communication"]},
            {"name": "Campus Placement Process Modernization", "description": "Created detailed Product Requirements Document (PRD) and Jira epics coordinating cross-departmental teams.", "technologies_used": ["Agile", "Scrum", "Requirements", "Leadership"]},
        ],
        "experience": [
            {"company": "Apex Strategy Consulting", "role": "Product & Analytics Intern", "duration": "Jan 2024 - Jun 2024", "description": "Facilitated daily standups and sprint retrospectives, delivering 6 milestone releases ahead of schedule."}
        ],
        "certifications": ["Certified Scrum Product Owner (CSPO)", "Google Data Analytics Professional Certificate"],
    },
]


def generate_resume_text(name: str, email: str, dept: str, cgpa: float, tpl: dict) -> str:
    """Format a realistic resume text matching the template."""
    skills_str = ", ".join(tpl["skills"])
    projects_str = "\n".join(
        f"- {p['name']}: {p['description']} (Tech: {', '.join(p['technologies_used'])})"
        for p in tpl["projects"]
    )
    exp_str = "\n".join(
        f"- {e['role']} at {e['company']} ({e['duration']}): {e['description']}"
        for e in tpl["experience"]
    )
    certs_str = ", ".join(tpl["certifications"])

    return f"""================================================================================
{name.upper()}
Email: {email} | Department: {dept} | CGPA: {cgpa}
================================================================================

PROFESSIONAL SUMMARY:
{tpl["summary"]}

TECHNICAL & PROFESSIONAL COMPETENCIES:
{skills_str}

EDUCATION:
Bachelor of Technology in {dept} (2021 - 2025)
Institution: National Institute of Engineering & Technology
Cumulative Grade Point Average: {cgpa} / 10.0

KEY TECHNICAL PROJECTS:
{projects_str}

WORK & INTERNSHIP EXPERIENCE:
{exp_str}

CERTIFICATIONS & ACHIEVEMENTS:
{certs_str}
================================================================================"""


def seed_candidates(db, target_count: int = 100) -> dict:
    """
    Seeds up to target_count diverse candidates into the database.
    Calculates match results against all existing jobs.
    """
    cached_password_hash = hash_password("student123")
    jobs = db.query(Job).all()

    created_candidates = []
    skipped_count = 0

    for idx, (name, email, dept, cgpa) in enumerate(NAMES[:target_count]):
        # Check if already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            skipped_count += 1
            continue

        # Create User
        user = User(
            name=name,
            email=email,
            password_hash=cached_password_hash,
            role="student",
        )
        db.add(user)
        db.flush()

        # Select corresponding cluster template
        cluster_idx = idx // 10
        tpl = CLUSTER_TEMPLATES[cluster_idx % len(CLUSTER_TEMPLATES)]

        resume_text = generate_resume_text(name, email, dept, cgpa, tpl)
        parsed_json = {
            "skills": tpl["skills"],
            "education": [{
                "degree": f"B.Tech in {dept}",
                "institution": "National Institute of Engineering & Technology",
                "year": "2025",
                "cgpa": str(cgpa),
            }],
            "experience": tpl["experience"],
            "projects": tpl["projects"],
            "certifications": tpl["certifications"],
            "summary": tpl["summary"],
        }

        # Create Student profile
        student = Student(
            user_id=user.id,
            department=dept,
            cgpa=cgpa,
            resume_path=f"uploads/student_{user.id}_default_resume.txt",
            resume_text=resume_text,
            parsed_json=parsed_json,
        )
        db.add(student)
        db.flush()

        # Compute matches for all existing jobs
        for job in jobs:
            jd_info = job.parsed_json or {"required_skills": job.skills_required or []}
            scores = compute_match(
                resume_text,
                job.description,
                parsed_json,
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

        created_candidates.append({
            "id": student.id,
            "name": user.name,
            "email": user.email,
            "department": dept,
            "cgpa": cgpa,
            "skills_count": len(tpl["skills"]),
        })

    db.commit()

    return {
        "message": f"Successfully processed candidates: {len(created_candidates)} created, {skipped_count} skipped",
        "total_created": len(created_candidates),
        "total_skipped": skipped_count,
        "sample": created_candidates[:5],
    }
