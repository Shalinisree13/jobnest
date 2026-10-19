from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, 
    TextAreaField, SelectField, IntegerField, DateField, RadioField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange

CATEGORY_CHOICES = [
    ('IT & Software', 'IT & Software'),
    ('Finance & Accounting', 'Finance & Accounting'),
    ('Healthcare & Medicine', 'Healthcare & Medicine'),
    ('Marketing & Sales', 'Marketing & Sales'),
    ('Engineering', 'Engineering'),
    ('Human Resources', 'Human Resources'),
    ('Design & Creative', 'Design & Creative'),
    ('Operations & Management', 'Operations & Management'),
]

EMPLOYMENT_TYPE_CHOICES = [
    ('Full-time', 'Full-time'),
    ('Part-time', 'Part-time'),
    ('Remote', 'Remote'),
    ('Contract', 'Contract'),
    ('Internship', 'Internship'),
]

INDUSTRY_CHOICES = [
    ('Technology & Software', 'Technology & Software'),
    ('Finance & Fintech', 'Finance & Fintech'),
    ('Healthcare & Biotech', 'Healthcare & Biotech'),
    ('Digital Marketing', 'Digital Marketing'),
    ('E-Commerce & Retail', 'E-Commerce & Retail'),
    ('Engineering & Manufacturing', 'Engineering & Manufacturing'),
    ('Education & EdTech', 'Education & EdTech'),
    ('Consulting & Services', 'Consulting & Services'),
]

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(message="Please enter your full name."),
        Length(min=2, max=100, message="Full name must be between 2 and 100 characters.")
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message="Please enter your email."),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter a password."),
        Length(min=6, max=64, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])
    role = SelectField('Register As', choices=[
        ('job_seeker', 'Job Seeker (Looking for opportunities)'),
        ('employer', 'Employer / Recruiter (Hiring talent)')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message="Please enter your email address."),
        Email(message="Please enter a valid email.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter your password.")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class JobSeekerProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(message="Full name is required."),
        Length(min=2, max=100)
    ])
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=30)
    ])
    location = StringField('Current Location', validators=[
        Optional(),
        Length(max=120)
    ])
    headline = StringField('Professional Headline', validators=[
        Optional(),
        Length(max=160)
    ])
    education = TextAreaField('Education & Qualifications', validators=[Optional()])
    skills = TextAreaField('Key Skills (comma separated)', validators=[Optional()])
    experience = TextAreaField('Work Experience', validators=[Optional()])
    resume = FileField('Upload Resume (PDF Only, Max 5MB)', validators=[
        FileAllowed(['pdf'], 'Only PDF files are accepted!')
    ])
    submit = SubmitField('Save Profile')


class CompanyProfileForm(FlaskForm):
    company_name = StringField('Company Name', validators=[
        DataRequired(message="Company name is required."),
        Length(min=2, max=150)
    ])
    company_website = StringField('Website URL', validators=[
        Optional(),
        Length(max=200)
    ])
    location = StringField('Headquarters / Location', validators=[
        DataRequired(message="Location is required."),
        Length(min=2, max=120)
    ])
    industry = SelectField('Industry', choices=INDUSTRY_CHOICES, validators=[DataRequired()])
    company_description = TextAreaField('About Company', validators=[
        DataRequired(message="Please provide a brief company description."),
        Length(min=10, max=2500)
    ])
    submit = SubmitField('Save Company Profile')


class JobForm(FlaskForm):
    job_title = StringField('Job Title', validators=[
        DataRequired(message="Job title is required."),
        Length(min=3, max=150)
    ])
    category = SelectField('Job Category', choices=CATEGORY_CHOICES, validators=[DataRequired()])
    employment_type = SelectField('Employment Type', choices=EMPLOYMENT_TYPE_CHOICES, validators=[DataRequired()])
    location = StringField('Job Location', validators=[
        DataRequired(message="Location is required (e.g. San Francisco, CA or Remote)."),
        Length(max=120)
    ])
    salary_min = IntegerField('Minimum Salary ($/year)', validators=[Optional(), NumberRange(min=0)])
    salary_max = IntegerField('Maximum Salary ($/year)', validators=[Optional(), NumberRange(min=0)])
    required_skills = StringField('Required Skills (comma separated)', validators=[
        DataRequired(message="Please specify required skills."),
        Length(max=255)
    ])
    qualifications = TextAreaField('Qualifications & Requirements', validators=[
        DataRequired(message="Please outline candidate qualifications.")
    ])
    job_description = TextAreaField('Detailed Job Description', validators=[
        DataRequired(message="Please provide a thorough job description.")
    ])
    application_deadline = DateField('Application Deadline', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Listing Status', choices=[('Active', 'Active'), ('Closed', 'Closed')], default='Active')
    is_featured = BooleanField('Feature this job prominently on the homepage')
    submit = SubmitField('Publish Vacancy')


class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter / Personal Note', validators=[
        Optional(),
        Length(max=2500, message="Cover letter cannot exceed 2500 characters.")
    ])
    resume_choice = RadioField('Resume Source', choices=[
        ('profile', 'Use resume from my profile'),
        ('new', 'Upload a custom resume for this role')
    ], default='profile')
    resume_file = FileField('Upload Custom Resume (PDF Only, Max 5MB)', validators=[
        FileAllowed(['pdf'], 'Only PDF documents are allowed!')
    ])
    submit = SubmitField('Submit Application')


class StatusUpdateForm(FlaskForm):
    application_status = SelectField('Update Application Status', choices=[
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview Scheduled', 'Interview Scheduled'),
        ('Hired', 'Hired'),
        ('Rejected', 'Rejected')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')
