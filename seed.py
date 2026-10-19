import os
from datetime import datetime, timezone, date, timedelta
from app import create_app
from models import db, User, JobSeekerProfile, Company, Job, Application, PlatformActivity

def create_valid_pdf(filepath, title, candidate_name, summary_text):
    """Generates a valid, readable minimal PDF 1.4 document"""
    # Clean text to avoid parentheses issues in basic PDF streams
    clean_title = title.replace('(', '[').replace(')', ']')
    clean_name = candidate_name.replace('(', '[').replace(')', ']')
    clean_summary = summary_text.replace('(', '[').replace(')', ']')

    stream_content = (
        f"BT\n"
        f"/F1 22 Tf\n"
        f"50 730 Td\n"
        f"({clean_title}) Tj\n"
        f"ET\n"
        f"BT\n"
        f"/F1 14 Tf\n"
        f"50 700 Td\n"
        f"(Applicant: {clean_name}) Tj\n"
        f"ET\n"
        f"BT\n"
        f"/F1 11 Tf\n"
        f"50 660 Td\n"
        f"(Overview: {clean_summary}) Tj\n"
        f"ET\n"
        f"BT\n"
        f"/F1 10 Tf\n"
        f"50 620 Td\n"
        f"(Phone: +1 555-019-2834 | Email: verified.candidate@jobnest.com) Tj\n"
        f"ET\n"
        f"BT\n"
        f"/F1 10 Tf\n"
        f"50 590 Td\n"
        f"(Education: B.S. in Computer Science, Honors Graduate) Tj\n"
        f"ET\n"
        f"BT\n"
        f"/F1 10 Tf\n"
        f"50 560 Td\n"
        f"(Core Skills: Python, SQL, Cloud Architecture, Team Leadership) Tj\n"
        f"ET\n"
        f"BT\n"
        f"/F1 9 Tf\n"
        f"50 500 Td\n"
        f"(-- JobNest Verified Candidate Profile Document --) Tj\n"
        f"ET\n"
    ).encode('latin1')

    stream_len = len(stream_content)

    body = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
        b"2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n"
        b"3 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R>>\nendobj\n"
        b"4 0 obj\n<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>\nendobj\n"
        b"5 0 obj\n<</Length " + str(stream_len).encode('ascii') + b">>\nstream\n" +
        stream_content +
        b"endstream\nendobj\n"
    )

    xref = (
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000228 00000 n \n"
        b"0000000295 00000 n \n"
        b"trailer\n<</Size 6 /Root 1 0 R>>\nstartxref\n" +
        str(len(body)).encode('ascii') +
        b"\n%%EOF\n"
    )

    with open(filepath, 'wb') as f:
        f.write(body + xref)

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing tables and recreate
        db.drop_all()
        db.create_all()

        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)

        now = datetime.now(timezone.utc)
        today = date.today()

        print("Seeding Users...")
        # 1. Administrator
        admin = User(
            full_name="JobNest Platform Administrator",
            email="admin@jobnest.com",
            role="admin"
        )
        admin.set_password("Admin@12345")
        db.session.add(admin)

        # 2. Employers
        emp1 = User(full_name="Sarah Jenkins", email="employer1@techinnovations.com", role="employer")
        emp1.set_password("Employer@12345")
        db.session.add(emp1)

        emp2 = User(full_name="Marcus Vance", email="employer2@healthfirst.com", role="employer")
        emp2.set_password("Employer@12345")
        db.session.add(emp2)

        emp3 = User(full_name="Elena Rostova", email="employer3@apexfinance.com", role="employer")
        emp3.set_password("Employer@12345")
        db.session.add(emp3)

        emp4 = User(full_name="Jordan Reed", email="employer4@nextgenmedia.com", role="employer")
        emp4.set_password("Employer@12345")
        db.session.add(emp4)

        # 3. Job Seekers
        seeker1 = User(full_name="Alex Morgan", email="alex.morgan@email.com", role="job_seeker")
        seeker1.set_password("Seeker@12345")
        db.session.add(seeker1)

        seeker2 = User(full_name="Sophia Chen", email="sophia.chen@email.com", role="job_seeker")
        seeker2.set_password("Seeker@12345")
        db.session.add(seeker2)

        seeker3 = User(full_name="David Kumar", email="david.kumar@email.com", role="job_seeker")
        seeker3.set_password("Seeker@12345")
        db.session.add(seeker3)

        seeker4 = User(full_name="Emily Davis", email="emily.davis@email.com", role="job_seeker")
        seeker4.set_password("Seeker@12345")
        db.session.add(seeker4)

        db.session.flush()

        print("Creating Companies...")
        comp1 = Company(
            employer_id=emp1.id,
            company_name="CloudScale Technologies",
            company_website="https://cloudscaletech.io",
            location="San Francisco, CA",
            industry="Technology & Software",
            company_description="CloudScale Technologies is a leading provider of enterprise cloud infrastructure and developer tooling. We build high-throughput systems trusted by Fortune 500 engineering teams."
        )
        comp2 = Company(
            employer_id=emp2.id,
            company_name="HealthFirst Global",
            company_website="https://healthfirstglobal.org",
            location="Boston, MA",
            industry="Healthcare & Biotech",
            company_description="HealthFirst Global leads healthcare innovation through digital patient management, medical research platforms, and biotechnology breakthroughs."
        )
        comp3 = Company(
            employer_id=emp3.id,
            company_name="Apex Capital Partners",
            company_website="https://apexcapital.com",
            location="New York, NY",
            industry="Finance & Fintech",
            company_description="Apex Capital Partners is an international financial analytics and investment advisory institution powering automated trading, wealth solutions, and risk modeling."
        )
        comp4 = Company(
            employer_id=emp4.id,
            company_name="NextGen Growth Agency",
            company_website="https://nextgenagency.co",
            location="Austin, TX",
            industry="Digital Marketing",
            company_description="NextGen Growth Agency is a hyper-growth brand strategy and digital marketing collective helping modern SaaS startups scale their customer acquisition."
        )
        db.session.add_all([comp1, comp2, comp3, comp4])
        db.session.flush()

        print("Generating Sample Resumes...")
        resume1_name = f"user_{seeker1.id}_alex_morgan_resume.pdf"
        create_valid_pdf(
            os.path.join(upload_dir, resume1_name),
            "Alex Morgan - Senior Full Stack Engineer Resume",
            "Alex Morgan",
            "Experienced software architect with 6+ years building distributed Python and TypeScript applications."
        )

        resume2_name = f"user_{seeker2.id}_sophia_chen_resume.pdf"
        create_valid_pdf(
            os.path.join(upload_dir, resume2_name),
            "Sophia Chen - Digital Product Marketing Specialist Resume",
            "Sophia Chen",
            "Performance marketer with proven track record scaling B2B SaaS revenue and multi-channel campaigns."
        )

        resume3_name = f"user_{seeker3.id}_david_kumar_resume.pdf"
        create_valid_pdf(
            os.path.join(upload_dir, resume3_name),
            "David Kumar - Senior Financial & Data Analyst Resume",
            "David Kumar",
            "Financial modeling specialist, CFA charterholder with deep background in forecasting and Power BI."
        )

        print("Creating Seeker Profiles...")
        prof1 = JobSeekerProfile(
            user_id=seeker1.id,
            phone="+1 (415) 890-1234",
            location="San Francisco, CA (Remote Open)",
            headline="Senior Full Stack Software Engineer | Python, React, AWS",
            education="B.S. in Computer Science - University of California, Berkeley (2018)",
            skills="Python, Flask, Django, PostgreSQL, Docker, Kubernetes, React, TypeScript, REST APIs",
            experience="5+ years as Senior Software Engineer at FinTech Labs. Built payment orchestration services handling $20M+ monthly transactions.",
            resume_filename=resume1_name
        )
        prof2 = JobSeekerProfile(
            user_id=seeker2.id,
            phone="+1 (512) 345-6789",
            location="Austin, TX",
            headline="Lead Growth Marketing Specialist | SaaS & Brand Strategy",
            education="B.A. in Marketing & Communications - UT Austin (2019)",
            skills="Growth Strategy, SEO/SEM, Google Analytics 4, Hubspot, Content Strategy, Performance Marketing",
            experience="4 years driving demand generation at Venture Media. Increased lead volume by 140% year-over-year.",
            resume_filename=resume2_name
        )
        prof3 = JobSeekerProfile(
            user_id=seeker3.id,
            phone="+1 (212) 555-8822",
            location="New York, NY",
            headline="Financial Analyst & Business Intelligence Specialist",
            education="M.S. in Financial Engineering - Columbia University (2020)",
            skills="Financial Modeling, Python, SQL, Tableau, Risk Analysis, Forecasting, Excel VBA",
            experience="4 years in quantitative risk and financial reporting at Global Asset Partners.",
            resume_filename=resume3_name
        )
        prof4 = JobSeekerProfile(
            user_id=seeker4.id,
            phone="+1 (617) 778-9900",
            location="Boston, MA",
            headline="Clinical Research Coordinator & Healthcare Operations",
            education="B.S. in Health Sciences - Boston University (2021)",
            skills="Clinical Trials, GCP Guidelines, Patient Protocol, EHR Management, Data Integrity",
            experience="3 years coordinating multi-phase oncology clinical trials at Boston Health Institute.",
            resume_filename=None
        )
        db.session.add_all([prof1, prof2, prof3, prof4])
        db.session.flush()

        print("Seeding Job Vacancies...")
        jobs_data = [
            Job(
                employer_id=emp1.id,
                company_id=comp1.id,
                job_title="Senior Python / Flask Backend Engineer",
                category="IT & Software",
                employment_type="Remote",
                location="Remote (US & Canada)",
                salary_min=125000,
                salary_max=160000,
                required_skills="Python, Flask, PostgreSQL, Redis, Docker, REST APIs, Microservices",
                qualifications="5+ years experience building backend APIs. Proven expertise in relational databases, caching, and scalable web architectures.",
                job_description="We are seeking an experienced Backend Engineer to design and maintain core APIs powering our enterprise cloud orchestrator. You will collaborate closely with frontend engineers, SREs, and product managers to deliver rock-solid, secure, and performant web services.",
                application_deadline=today + timedelta(days=30),
                status="Active",
                is_featured=True
            ),
            Job(
                employer_id=emp1.id,
                company_id=comp1.id,
                job_title="Lead Frontend UI/UX Developer",
                category="IT & Software",
                employment_type="Full-time",
                location="San Francisco, CA",
                salary_min=130000,
                salary_max=165000,
                required_skills="JavaScript, TypeScript, React, HTML5, CSS3, Tailwind CSS, Webpack",
                qualifications="Strong proficiency in modern JavaScript, component design systems, and web performance optimization.",
                job_description="Join our front-of-house team to craft gorgeous, accessible, and ultra-fast user experiences for tens of thousands of developer clients worldwide.",
                application_deadline=today + timedelta(days=25),
                status="Active",
                is_featured=True
            ),
            Job(
                employer_id=emp2.id,
                company_id=comp2.id,
                job_title="Clinical Research Project Manager",
                category="Healthcare & Medicine",
                employment_type="Full-time",
                location="Boston, MA",
                salary_min=95000,
                salary_max=125000,
                required_skills="Clinical Trials, GCP, Protocol Management, Healthcare Data, Team Leadership",
                qualifications="Master's or Bachelor's degree in Life Sciences or Healthcare Administration with 4+ years managing medical trials.",
                job_description="Lead clinical trial operations across partner medical institutions. Ensure strict protocol adherence, patient safety compliance, and coordinate multi-disciplinary scientific teams.",
                application_deadline=today + timedelta(days=40),
                status="Active",
                is_featured=True
            ),
            Job(
                employer_id=emp3.id,
                company_id=comp3.id,
                job_title="Senior Financial Analyst & Modeler",
                category="Finance & Accounting",
                employment_type="Full-time",
                location="New York, NY",
                salary_min=110000,
                salary_max=145000,
                required_skills="Financial Modeling, Valuation, Forecasting, SQL, Power BI, Advanced Excel",
                qualifications="Bachelor's in Finance, Economics, or related quantitative field. 3-5 years in investment banking, corporate finance, or equity research.",
                job_description="Conduct valuation models, review strategic investment opportunities, and prepare executive presentations for our investment committee.",
                application_deadline=today + timedelta(days=20),
                status="Active",
                is_featured=True
            ),
            Job(
                employer_id=emp4.id,
                company_id=comp4.id,
                job_title="Growth Marketing & Acquisition Manager",
                category="Marketing & Sales",
                employment_type="Full-time",
                location="Austin, TX (Hybrid)",
                salary_min=85000,
                salary_max=115000,
                required_skills="Growth Hacking, Paid Media, Google Ads, SEO, Conversion Rate Optimization, A/B Testing",
                qualifications="Demonstrated track record of scaling digital acquisition channels with measurable ROAS in high-growth environments.",
                job_description="Architect, launch, and optimize acquisition funnels across search, paid social, and content channels to drive sustainable ARR growth.",
                application_deadline=today + timedelta(days=35),
                status="Active",
                is_featured=True
            ),
            Job(
                employer_id=emp1.id,
                company_id=comp1.id,
                job_title="Cloud Infrastructure & DevOps Engineer",
                category="Engineering",
                employment_type="Remote",
                location="Remote",
                salary_min=135000,
                salary_max=170000,
                required_skills="AWS, Terraform, Kubernetes, Linux, CI/CD, Prometheus, Security",
                qualifications="Solid understanding of Linux internals, immutable infrastructure as code, and zero-downtime deployment pipelines.",
                job_description="Automate and scale our multi-region AWS footprint. Build resilient CI/CD pipelines and uphold 99.99% availability standards.",
                application_deadline=today + timedelta(days=45),
                status="Active",
                is_featured=False
            ),
            Job(
                employer_id=emp4.id,
                company_id=comp4.id,
                job_title="People Operations & Talent Specialist",
                category="Human Resources",
                employment_type="Full-time",
                location="Austin, TX",
                salary_min=65000,
                salary_max=85000,
                required_skills="Technical Recruiting, Onboarding, Employee Relations, HRIS, Talent Sourcing",
                qualifications="2+ years in recruitment or people ops within a tech or agency setting.",
                job_description="Champion our recruitment pipeline, manage candidate interviews, and cultivate a supportive, high-performance company culture.",
                application_deadline=today + timedelta(days=15),
                status="Active",
                is_featured=False
            ),
            Job(
                employer_id=emp4.id,
                company_id=comp4.id,
                job_title="Product & Brand Visual Designer",
                category="Design & Creative",
                employment_type="Contract",
                location="Remote",
                salary_min=75000,
                salary_max=100000,
                required_skills="Figma, Adobe Creative Suite, Design Systems, Typography, Wireframing",
                qualifications="Exceptional portfolio showcasing web apps, responsive design, and branding systems.",
                job_description="Design clean, impactful digital interfaces and marketing visuals that elevate brand perception across touchpoints.",
                application_deadline=today + timedelta(days=18),
                status="Active",
                is_featured=False
            ),
            Job(
                employer_id=emp2.id,
                company_id=comp2.id,
                job_title="Healthcare Operations & Quality Director",
                category="Operations & Management",
                employment_type="Full-time",
                location="Boston, MA",
                salary_min=120000,
                salary_max=155000,
                required_skills="Healthcare Operations, Lean Six Sigma, Compliance, Budgeting, Cross-functional Leadership",
                qualifications="7+ years leadership experience overseeing healthcare facility or clinical trial logistics.",
                job_description="Oversee daily operational workflows, enhance patient service delivery, and maintain strict healthcare regulatory standards.",
                application_deadline=today + timedelta(days=28),
                status="Active",
                is_featured=False
            )
        ]
        db.session.add_all(jobs_data)
        db.session.flush()

        print("Seeding Initial Applications...")
        # 1. Alex applied to Senior Python Backend
        app1 = Application(
            job_id=jobs_data[0].id,
            job_seeker_id=seeker1.id,
            resume_filename=resume1_name,
            cover_letter="Dear Hiring Manager,\n\nI am thrilled to apply for the Senior Python/Flask Backend Engineer role. Having spent over five years developing distributed Python microservices, I am confident in my ability to immediately contribute to CloudScale's infrastructure.\n\nBest regards,\nAlex Morgan",
            application_status="Interview Scheduled",
            applied_at=now - timedelta(days=4)
        )

        # 2. Sophia applied to Growth Marketing Manager
        app2 = Application(
            job_id=jobs_data[4].id,
            job_seeker_id=seeker2.id,
            resume_filename=resume2_name,
            cover_letter="Hi Team,\n\nI have been tracking NextGen's impressive expansion in the SaaS domain. With my background executing multi-channel performance marketing funnels, I would love the chance to scale your customer acquisition.\n\nSincerely,\nSophia Chen",
            application_status="Shortlisted",
            applied_at=now - timedelta(days=2)
        )

        # 3. David applied to Senior Financial Analyst
        app3 = Application(
            job_id=jobs_data[3].id,
            job_seeker_id=seeker3.id,
            resume_filename=resume3_name,
            cover_letter="Dear Apex Capital Team,\n\nAs a financial modeler with deep experience in quantitative risk analysis and financial forecasting, I am excited about the opportunity to support your investment strategies.\n\nThank you,\nDavid Kumar",
            application_status="Under Review",
            applied_at=now - timedelta(days=1)
        )
        db.session.add_all([app1, app2, app3])

        print("Seeding Platform Audit Activity Logs...")
        activities = [
            PlatformActivity(user_id=admin.id, action="SYSTEM_INIT", description="JobNest platform initialized with secure database schema"),
            PlatformActivity(user_id=emp1.id, action="JOB_POSTED", description="CloudScale Technologies published 'Senior Python / Flask Backend Engineer'"),
            PlatformActivity(user_id=emp2.id, action="JOB_POSTED", description="HealthFirst Global published 'Clinical Research Project Manager'"),
            PlatformActivity(user_id=emp3.id, action="JOB_POSTED", description="Apex Capital Partners published 'Senior Financial Analyst & Modeler'"),
            PlatformActivity(user_id=seeker1.id, action="APPLICATION_SUBMITTED", description="Alex Morgan submitted application for 'Senior Python / Flask Backend Engineer'"),
            PlatformActivity(user_id=emp1.id, action="STATUS_CHANGE", description="CloudScale Technologies scheduled interview with Alex Morgan"),
            PlatformActivity(user_id=seeker2.id, action="APPLICATION_SUBMITTED", description="Sophia Chen submitted application for 'Growth Marketing & Acquisition Manager'"),
            PlatformActivity(user_id=emp4.id, action="STATUS_CHANGE", description="NextGen Growth Agency shortlisted Sophia Chen")
        ]
        db.session.add_all(activities)

        db.session.commit()
        print("Database seeded successfully with all roles, jobs, applications, and valid PDF resumes!")

if __name__ == '__main__':
    seed_database()
