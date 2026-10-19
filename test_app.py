import os
import unittest
import io
from app import create_app
from models import db, User, Job, Company, Application, JobSeekerProfile
from sqlalchemy.pool import StaticPool
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for programmatic testing
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': StaticPool,
        'connect_args': {'check_same_thread': False}
    }

class JobNestTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed initial test data
        self.admin = User(full_name="Admin Test", email="admin@test.com", role="admin")
        self.admin.set_password("Admin@12345")

        self.employer = User(full_name="Employer Test", email="emp@test.com", role="employer")
        self.employer.set_password("Emp@12345")

        self.seeker = User(full_name="Seeker Test", email="seeker@test.com", role="job_seeker")
        self.seeker.set_password("Seeker@12345")

        db.session.add_all([self.admin, self.employer, self.seeker])
        db.session.flush()

        self.company = Company(
            employer_id=self.employer.id,
            company_name="Test Enterprise Inc",
            location="San Francisco, CA",
            industry="Technology & Software",
            company_description="Top tech firm"
        )
        self.profile = JobSeekerProfile(
            user_id=self.seeker.id,
            phone="+1 555-0100",
            location="San Francisco, CA",
            skills="Python, Flask, JavaScript",
            resume_filename="user_test_resume.pdf"
        )
        db.session.add_all([self.company, self.profile])
        db.session.flush()

        self.job = Job(
            employer_id=self.employer.id,
            company_id=self.company.id,
            job_title="Software Developer",
            category="IT & Software",
            location="San Francisco, CA",
            employment_type="Full-time",
            salary_min=100000,
            salary_max=130000,
            required_skills="Python, Flask",
            qualifications="CS degree",
            job_description="Great development opportunity",
            status="Active"
        )
        db.session.add(self.job)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Find Your Dream Job with", response.data)
        self.assertIn(b"Software Developer", response.data)

    def test_job_search(self):
        response = self.client.get('/jobs?q=Software')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Software Developer", response.data)

        # Non-matching search
        response_empty = self.client.get('/jobs?q=NonExistentSkill123')
        self.assertEqual(response_empty.status_code, 200)
        self.assertIn(b"No Job Postings Found", response_empty.data)

    def test_job_details(self):
        response = self.client.get(f'/jobs/{self.job.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Software Developer", response.data)
        self.assertIn(b"Test Enterprise Inc", response.data)

    def test_authentication_flow(self):
        # Register new job seeker
        reg_response = self.client.post('/register', data=dict(
            full_name="New Seeker",
            email="newseeker@test.com",
            password="Password@123",
            confirm_password="Password@123",
            role="job_seeker"
        ), follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b"Welcome to JobNest", reg_response.data)

        # Login
        self.logout()
        login_res = self.login("newseeker@test.com", "Password@123")
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Welcome back, New Seeker!", login_res.data)

    def test_role_authorization_protection(self):
        # Unauthenticated user cannot access admin
        res = self.client.get('/admin', follow_redirects=True)
        self.assertIn(b"Please sign in to access this page", res.data)

        # Job seeker cannot access admin
        self.login("seeker@test.com", "Seeker@12345")
        res_seeker_admin = self.client.get('/admin', follow_redirects=True)
        self.assertIn(b"You do not have permission to access that resource", res_seeker_admin.data)

        # Job seeker cannot post a job
        res_post_job = self.client.get('/jobs/new', follow_redirects=True)
        self.assertIn(b"You do not have permission to access that resource", res_post_job.data)
        self.logout()

        # Admin CAN access admin
        self.login("admin@test.com", "Admin@12345")
        res_admin = self.client.get('/admin')
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b"Administrator Control Center", res_admin.data)
        self.logout()

    def test_application_lifecycle(self):
        # Login as job seeker
        self.login("seeker@test.com", "Seeker@12345")

        # Submit application using profile resume
        apply_res = self.client.post(f'/jobs/{self.job.id}/apply', data=dict(
            resume_choice='profile',
            cover_letter='I am very interested in this software developer position.'
        ), follow_redirects=True)
        self.assertEqual(apply_res.status_code, 200)
        self.assertIn(b"Your application for Software Developer has been successfully submitted", apply_res.data)

        # Verify application in DB
        app_record = Application.query.filter_by(job_id=self.job.id, job_seeker_id=self.seeker.id).first()
        self.assertIsNotNone(app_record)
        self.assertEqual(app_record.application_status, 'Under Review')

        # Prevent duplicate applications
        dup_res = self.client.post(f'/jobs/{self.job.id}/apply', data=dict(
            resume_choice='profile',
            cover_letter='Duplicate attempt'
        ), follow_redirects=True)
        self.assertIn(b"You have already submitted an application for this position", dup_res.data)

        self.logout()

        # Employer reviews application & updates status to Shortlisted
        self.login("emp@test.com", "Emp@12345")
        applicants_res = self.client.get(f'/employer/jobs/{self.job.id}/applicants')
        self.assertEqual(applicants_res.status_code, 200)
        self.assertIn(b"Seeker Test", applicants_res.data)

        # Update status
        status_res = self.client.post(f'/employer/applications/{app_record.id}/status', data=dict(
            application_status='Shortlisted'
        ), follow_redirects=True)
        self.assertEqual(status_res.status_code, 200)

        db.session.refresh(app_record)
        self.assertEqual(app_record.application_status, 'Shortlisted')
        self.logout()

        # Seeker sees updated status in dashboard
        self.login("seeker@test.com", "Seeker@12345")
        seeker_dash = self.client.get('/seeker/dashboard')
        self.assertIn(b"Shortlisted", seeker_dash.data)

        # Seeker withdraws application
        withdraw_res = self.client.post(f'/seeker/applications/{app_record.id}/withdraw', follow_redirects=True)
        self.assertEqual(withdraw_res.status_code, 200)
        self.assertIn(b"Your application has been withdrawn", withdraw_res.data)

        db.session.refresh(app_record)
        self.assertEqual(app_record.application_status, 'Withdrawn')

    def test_employer_job_crud(self):
        self.login("emp@test.com", "Emp@12345")

        # Post new job
        post_res = self.client.post('/jobs/new', data=dict(
            job_title="Frontend Specialist",
            category="IT & Software",
            employment_type="Remote",
            location="Remote",
            salary_min=95000,
            salary_max=120000,
            required_skills="React, TypeScript, CSS",
            qualifications="3+ years experience",
            job_description="Create high performance UI interfaces",
            status="Active"
        ), follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)
        self.assertIn(b"Frontend Specialist", post_res.data)

        created_job = Job.query.filter_by(job_title="Frontend Specialist").first()
        self.assertIsNotNone(created_job)

        # Edit job
        edit_res = self.client.post(f'/jobs/{created_job.id}/edit', data=dict(
            job_title="Senior Frontend Specialist",
            category="IT & Software",
            employment_type="Remote",
            location="Remote",
            salary_min=110000,
            salary_max=140000,
            required_skills="React, TypeScript, Next.js",
            qualifications="4+ years experience",
            job_description="Updated description",
            status="Active"
        ), follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        db.session.refresh(created_job)
        self.assertEqual(created_job.job_title, "Senior Frontend Specialist")

        # Delete job
        del_res = self.client.post(f'/jobs/{created_job.id}/delete', follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIsNone(db.session.get(Job, created_job.id))

    def test_admin_governance(self):
        self.login("admin@test.com", "Admin@12345")

        # Admin views users
        users_res = self.client.get('/admin/users')
        self.assertEqual(users_res.status_code, 200)
        self.assertIn(b"Seeker Test", users_res.data)
        self.assertIn(b"Employer Test", users_res.data)

        # Admin toggles user account status
        toggle_res = self.client.post(f'/admin/users/{self.seeker.id}/toggle-status', follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)
        db.session.refresh(self.seeker)
        self.assertFalse(self.seeker.is_active)

        # Admin moderates jobs
        jobs_res = self.client.get('/admin/jobs')
        self.assertEqual(jobs_res.status_code, 200)
        self.assertIn(b"Software Developer", jobs_res.data)

        # Toggle featured
        feat_res = self.client.post(f'/admin/jobs/{self.job.id}/toggle-featured', follow_redirects=True)
        self.assertEqual(feat_res.status_code, 200)
        db.session.refresh(self.job)
        self.assertTrue(self.job.is_featured)

if __name__ == '__main__':
    unittest.main()
