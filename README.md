# JobNest – Online Job Portal and Recruitment System

**JobNest** is an enterprise-grade, modern, and fully functional online recruitment and job portal web application built with **Python (Flask)**, **SQLite**, and **HTML5/CSS3/JavaScript**. 

It connects qualified job seekers with premier employers through streamlined vacancy discovery, role-based workflows, resume file validation, application tracking, and administrator governance.

---

## 🌟 Key Features

### 👤 1. Job Seeker (Candidate)
- **Authentication**: Secure account registration and session-based login.
- **Candidate Profile**: Manage contact details, professional headline, skills tags, education, work experience, and location.
- **PDF Resume Upload**: Secure upload of resumes in PDF format with file-header validation (magic bytes), 5MB size limits, and UUID-based safe storage.
- **Job Discovery & Search**: Filter vacancies dynamically by keyword, location, industry category, employment type (Remote, Full-time, etc.), and salary sorting.
- **Job Details & One-Click Apply**: View detailed specifications, company backgrounds, deadlines, and apply either with a profile resume or a custom PDF resume + cover letter.
- **Application Tracking**: Live dashboard displaying application statuses (*Under Review*, *Shortlisted*, *Interview Scheduled*, *Hired*, *Rejected*).
- **Withdraw Application**: Self-service withdrawal option for active applications.
- **Smart Recommendations**: Automatic job matching based on candidate skills.

### 🏢 2. Employer / Recruiter
- **Company Branding**: Build and maintain an attractive company profile (description, location, website URL, industry).
- **Post Job Vacancies**: Publish openings with category tags, salary ranges, employment types, required skills, qualifications, descriptions, and deadlines.
- **Listing Governance**: Edit postings, toggle status (*Active* / *Closed*), or delete listings.
- **Candidate Review**: Dedicated applicant management dashboard for each job posting.
- **Resume Access**: Authenticated, secure viewing and downloading of candidate PDF resumes.
- **Status Updates**: Instantly update applicant statuses to *Under Review*, *Shortlisted*, *Interview Scheduled*, *Hired*, or *Rejected*.

### 🛡️ 3. Platform Administrator
- **Protected Hub**: Restricted strictly to users with the `admin` role.
- **Platform Analytics**: Total users, candidate count, employer count, active vs. closed jobs, and total applications.
- **Interactive Visualizations**: Dynamic Chart.js charts showing application status distributions and job counts by category.
- **User Governance**: Browse all registered users, filter by role, activate/suspend accounts, and delete users.
- **Job Moderation**: Review all listings across companies, toggle homepage featured placement, and remove invalid postings.
- **Audit Activity Trail**: Real-time log of platform events (registrations, job posts, status updates, applications).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask 3.x |
| **Database** | SQLite with Flask-SQLAlchemy (ORM) |
| **Templates** | Jinja2 with custom filters (`timeago`, `format_date`, `status_badge_class`) |
| **Forms & Security** | Flask-WTF, WTForms, CSRF Protection, Werkzeug Security (PBKDF2/Scrypt) |
| **File Handling** | Python `secure_filename`, UUID prefixing, PDF Magic-Byte validation |
| **Frontend** | HTML5, Modern CSS3 (Flexbox, CSS Grid, Custom Properties), JavaScript (ES6) |
| **Data Visualizations** | Chart.js |

---

## 📂 Project Structure

```text
jobnest/
├── app.py                     # Application factory, filters, error handlers, and blueprints
├── config.py                  # Database URI, upload directories, security configs
├── models.py                  # SQLAlchemy models (User, JobSeekerProfile, Company, Job, Application, Activity)
├── forms.py                   # Flask-WTF form classes with validation
├── utils.py                   # Role decorators, PDF validator, file storage helper, audit logger
├── seed.py                    # Database seeder with realistic test data & valid PDF resumes
├── test_app.py                # Automated unit and integration test suite
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation & setup instructions
├── routes/
│   ├── auth.py                # Login, registration, and logout routes
│   ├── main.py                # Homepage, about, contact, legal, secure resume endpoint
│   ├── jobs.py                # Browse, filter, details, apply, post, edit, delete jobs
│   ├── seeker.py              # Candidate dashboard, profile, and application withdrawal
│   ├── employer.py            # Employer dashboard, company profile, applicants review
│   └── admin.py               # Administrator analytics, user governance, job moderation
├── static/
│   ├── css/
│   │   ├── style.css          # Design system, typography, hero, cards, forms, modals
│   │   ├── dashboard.css      # Dashboard layouts, sidebar, stat cards, tables
│   │   └── responsive.css     # Mobile and tablet breakpoints
│   └── js/
│       ├── script.js          # Interactive modals, file upload preview, dropdowns
│       └── charts.js          # Chart.js analytics rendering
├── templates/
│   ├── base.html              # Base layout with navbar, alerts, footer
│   ├── index.html             # Homepage with hero search, categories, featured jobs
│   ├── about.html             # About platform
│   ├── contact.html           # Contact & support
│   ├── privacy.html           # Privacy policy
│   ├── terms.html             # Terms of service
│   ├── 404.html, 403.html, 500.html # Error pages
│   ├── auth/                  # login.html, register.html
│   ├── jobs/                  # index.html, details.html, post.html, edit.html
│   ├── seeker/                # dashboard.html, profile.html
│   ├── employer/              # dashboard.html, company.html, applicants.html
│   └── admin/                 # dashboard.html, users.html, jobs.html
├── instance/
│   └── jobnest.db             # SQLite database file
└── uploads/
    └── resumes/               # Securely stored candidate PDF resumes
```

---

## 🚀 How to Run in VS Code on Windows

Follow these simple steps to run JobNest on your Windows PC using Visual Studio Code.

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** > **Open Folder...**
3. Select the `jobnest` folder located at:
   ```text
   C:\Users\shali\.gemini\antigravity\scratch\jobnest
   ```
4. Open the integrated terminal in VS Code by pressing ``Ctrl + ` `` (or **Terminal** > **New Terminal**).

### Step 2: Create and Activate a Virtual Environment (Recommended)
In the VS Code terminal (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If you see an execution policy prompt, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Seed the Database with Realistic Demo Data
Populate the database with pre-configured users, companies, jobs across all categories, valid PDF resumes, and platform activities:
```powershell
python seed.py
```

### Step 5: Start the Flask Web Server
```powershell
python app.py
```
You will see output similar to:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 6: Open in Your Browser
Open your preferred web browser (Chrome, Edge, Firefox) and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🔑 Pre-Configured Demo Accounts

For immediate testing, the database includes pre-seeded accounts for each role:

| Role | Email Address | Password | Description |
|---|---|---|---|
| **Administrator** | `admin@jobnest.com` | `Admin@12345` | Full access to platform KPIs, charts, user management, and job moderation |
| **Employer** | `employer1@techinnovations.com` | `Employer@12345` | CloudScale Technologies recruiter; manage jobs and review applicants |
| **Employer** | `employer2@healthfirst.com` | `Employer@12345` | HealthFirst Global recruiter; post healthcare vacancies |
| **Job Seeker** | `alex.morgan@email.com` | `Seeker@12345` | Senior Full-Stack Engineer with attached PDF resume and active applications |
| **Job Seeker** | `sophia.chen@email.com` | `Seeker@12345` | Growth Marketing Specialist with attached PDF resume |

*(You can also click **Get Started** on the homepage to register brand new Seeker or Employer accounts).*

---

## 🔒 Security & Best Practices Implemented

1. **Password Encryption**: Stored exclusively using Werkzeug's secure hash generator (`generate_password_hash` using PBKDF2/Scrypt).
2. **Access Control**: Role-based access decorators (`@login_required`, `@role_required(...)`) strictly prohibit unauthorized access.
3. **Resume Protection**: Resumes are stored outside public static directories. The endpoint `/resumes/<filename>` validates whether the requester is the applicant themselves, the recruiter who received the application, or an admin.
4. **File Upload Security**:
   - Only `.pdf` extensions accepted.
   - Files are inspected for standard PDF magic header bytes (`%PDF-`).
   - File size enforced via `MAX_CONTENT_LENGTH` (5MB).
   - Filenames sanitized with `secure_filename` and prepended with random UUID tokens.
5. **CSRF Attack Defense**: Every web form is protected with Flask-WTF CSRF tokens.
6. **SQL Injection Defense**: All database queries are executed via SQLAlchemy parameterized queries.

---

## 🧪 Running Automated Tests

JobNest includes a full automated test suite verifying all routes, authorization protections, file validations, and CRUD operations:

```powershell
python test_app.py
```
Output:
```text
Ran 8 tests in 4.279s

OK
```

---

## 📄 License
This project is developed as part of the JobNest recruitment system. Feel free to use and extend it!
