from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='job_seeker')  # 'job_seeker', 'employer', 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    seeker_profile = db.relationship('JobSeekerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', backref='employer', uselist=False, cascade='all, delete-orphan')
    posted_jobs = db.relationship('Job', backref='employer', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='applicant', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_employer(self):
        return self.role == 'employer'

    @property
    def is_seeker(self):
        return self.role == 'job_seeker'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class JobSeekerProfile(db.Model):
    __tablename__ = 'job_seeker_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    headline = db.Column(db.String(160), nullable=True)  # e.g. "Senior Full-Stack Developer"
    education = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    def calculate_completion(self):
        """Calculates profile completion percentage based on filled fields"""
        fields = [
            bool(self.user.full_name),
            bool(self.user.email),
            bool(self.phone),
            bool(self.location),
            bool(self.headline),
            bool(self.education),
            bool(self.skills),
            bool(self.experience),
            bool(self.resume_filename)
        ]
        completed = sum(1 for f in fields if f)
        return int((completed / len(fields)) * 100)

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def __repr__(self):
        return f'<JobSeekerProfile user_id={self.user_id}>'


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    company_description = db.Column(db.Text, nullable=True)
    company_website = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    industry = db.Column(db.String(100), default='Technology')
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    jobs = db.relationship('Job', backref='company', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.company_name}>'


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, default='IT & Software', index=True)
    job_description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False, index=True)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    employment_type = db.Column(db.String(50), nullable=False, default='Full-time')  # Full-time, Part-time, Remote, Contract, Internship
    required_skills = db.Column(db.Text, nullable=True)
    qualifications = db.Column(db.Text, nullable=True)
    application_deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Active')  # Active, Closed
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_open(self):
        if self.status != 'Active':
            return False
        if self.application_deadline:
            from datetime import date
            if self.application_deadline < date.today():
                return False
        return True

    def get_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f} / year"
        elif self.salary_min:
            return f"From ${self.salary_min:,.0f} / year"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,.0f} / year"
        return "Salary Negotiable"

    def __repr__(self):
        return f'<Job {self.job_title} at {self.company_id}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)
    application_status = db.Column(
        db.String(30), 
        nullable=False, 
        default='Under Review'
    )  # 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Rejected', 'Hired', 'Withdrawn'
    applied_at = db.Column(db.DateTime, default=get_utc_now)

    __table_args__ = (
        db.UniqueConstraint('job_id', 'job_seeker_id', name='uq_job_application'),
    )

    def __repr__(self):
        return f'<Application job={self.job_id} seeker={self.job_seeker_id} status={self.application_status}>'


class PlatformActivity(db.Model):
    __tablename__ = 'platform_activity'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(80), nullable=False)  # 'REGISTER', 'JOB_POSTED', 'APPLICATION_SUBMITTED', 'STATUS_CHANGE', etc.
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))

    def __repr__(self):
        return f'<PlatformActivity {self.action}: {self.description}>'
