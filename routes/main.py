import os
from flask import Blueprint, render_template, current_app, abort, send_from_directory, flash, redirect, url_for
from sqlalchemy import func
from models import db, Job, Company, User, Application, JobSeekerProfile
from utils import get_current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Featured jobs for the homepage
    featured_jobs = Job.query.filter_by(status='Active', is_featured=True)\
        .order_by(Job.created_at.desc()).limit(6).all()
    
    # If fewer than 6 featured jobs, supplement with recent active jobs
    if len(featured_jobs) < 6:
        existing_ids = [j.id for j in featured_jobs]
        additional_jobs = Job.query.filter(Job.status == 'Active', ~Job.id.in_(existing_ids if existing_ids else [-1]))\
            .order_by(Job.created_at.desc()).limit(6 - len(featured_jobs)).all()
        featured_jobs = featured_jobs + additional_jobs

    # Recently posted jobs
    recent_jobs = Job.query.filter_by(status='Active')\
        .order_by(Job.created_at.desc()).limit(8).all()

    # Dynamic Category counts
    all_categories = [
        'IT & Software',
        'Finance & Accounting',
        'Healthcare & Medicine',
        'Marketing & Sales',
        'Engineering',
        'Human Resources',
        'Design & Creative',
        'Operations & Management'
    ]
    
    category_counts_query = db.session.query(
        Job.category, func.count(Job.id)
    ).filter(Job.status == 'Active').group_by(Job.category).all()
    
    counts_map = dict(category_counts_query)
    category_data = [
        {'name': cat, 'count': counts_map.get(cat, 0)}
        for cat in all_categories
    ]

    # Platform metrics for hero section
    total_active_jobs = Job.query.filter_by(status='Active').count()
    total_companies = Company.query.count()
    total_seekers = User.query.filter_by(role='job_seeker').count()

    return render_template(
        'index.html',
        featured_jobs=featured_jobs,
        recent_jobs=recent_jobs,
        category_data=category_data,
        total_active_jobs=total_active_jobs,
        total_companies=total_companies,
        total_seekers=total_seekers
    )


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    return render_template('contact.html')


@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@main_bp.route('/terms')
def terms():
    return render_template('terms.html')


@main_bp.route('/resumes/<filename>')
@login_required
def view_resume(filename):
    """Secure endpoint for viewing/downloading candidate resumes.
    Strictly checks ownership or authorization before serving file.
    """
    user = get_current_user()
    if not user:
        abort(401)

    # 1. Admin can view any resume
    if user.is_admin:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

    # 2. Check if this is the seeker's own profile resume
    if user.is_seeker and user.seeker_profile and user.seeker_profile.resume_filename == filename:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

    # 3. Check if this is an application resume submitted by this seeker
    if user.is_seeker:
        app_by_seeker = Application.query.filter_by(
            job_seeker_id=user.id, 
            resume_filename=filename
        ).first()
        if app_by_seeker:
            return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

    # 4. Check if the logged in employer received this resume for one of their jobs
    if user.is_employer:
        app_for_employer = Application.query.join(Job).filter(
            Job.employer_id == user.id,
            Application.resume_filename == filename
        ).first()
        if app_for_employer:
            return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

    # Unauthorized access attempt
    abort(403, description="Access denied. You do not have permission to view this resume.")
