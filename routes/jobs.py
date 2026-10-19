from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from sqlalchemy import or_, desc, asc
from models import db, Job, Company, Application, User, JobSeekerProfile
from forms import JobForm, ApplicationForm
from utils import get_current_user, login_required, role_required, save_resume, log_activity

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs')
def index():
    q = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip()
    category = request.args.get('category', '').strip()
    employment_type = request.args.get('employment_type', '').strip()
    company_filter = request.args.get('company', '').strip()
    sort = request.args.get('sort', 'newest')

    query = Job.query.filter(Job.status == 'Active')

    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Job.job_title.ilike(search_pattern),
                Job.required_skills.ilike(search_pattern),
                Job.job_description.ilike(search_pattern)
            )
        )

    if location:
        loc_pattern = f"%{location}%"
        query = query.filter(Job.location.ilike(loc_pattern))

    if category and category != 'All':
        query = query.filter(Job.category == category)

    if employment_type and employment_type != 'All':
        query = query.filter(Job.employment_type == employment_type)

    if company_filter:
        query = query.join(Company).filter(Company.company_name.ilike(f"%{company_filter}%"))

    # Sorting
    if sort == 'salary_high':
        query = query.order_by(desc(Job.salary_max.is_(None)), desc(Job.salary_max))
    elif sort == 'salary_low':
        query = query.order_by(desc(Job.salary_min.is_(None)), asc(Job.salary_min))
    elif sort == 'oldest':
        query = query.order_by(asc(Job.created_at))
    else:  # newest
        query = query.order_by(desc(Job.created_at))

    jobs = query.all()

    # Get distinct categories and employment types for filter dropdowns
    categories = [
        'IT & Software',
        'Finance & Accounting',
        'Healthcare & Medicine',
        'Marketing & Sales',
        'Engineering',
        'Human Resources',
        'Design & Creative',
        'Operations & Management'
    ]
    employment_types = ['Full-time', 'Part-time', 'Remote', 'Contract', 'Internship']

    return render_template(
        'jobs/index.html',
        jobs=jobs,
        q=q,
        location=location,
        selected_category=category,
        selected_employment_type=employment_type,
        categories=categories,
        employment_types=employment_types,
        sort=sort,
        total_results=len(jobs)
    )


@jobs_bp.route('/jobs/<int:job_id>')
def details(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)

    user = get_current_user()
    has_applied = False
    existing_application = None
    form = ApplicationForm()

    if user and user.is_seeker:
        existing_application = Application.query.filter_by(
            job_id=job.id,
            job_seeker_id=user.id
        ).first()
        has_applied = existing_application is not None

    # Similar jobs
    similar_jobs = Job.query.filter(
        Job.category == job.category,
        Job.id != job.id,
        Job.status == 'Active'
    ).limit(3).all()

    return render_template(
        'jobs/details.html',
        job=job,
        has_applied=has_applied,
        existing_application=existing_application,
        form=form,
        similar_jobs=similar_jobs
    )


@jobs_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
@role_required('job_seeker')
def apply(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)

    user = get_current_user()

    # 1. Verify job is active and open
    if not job.is_open:
        flash('Applications for this job listing are currently closed or have expired.', 'warning')
        return redirect(url_for('jobs.details', job_id=job.id))

    # 2. Check if already applied
    existing_app = Application.query.filter_by(job_id=job.id, job_seeker_id=user.id).first()
    if existing_app:
        flash('You have already submitted an application for this position.', 'info')
        return redirect(url_for('jobs.details', job_id=job.id))

    form = ApplicationForm()
    if form.validate_on_submit():
        resume_filename = None

        if form.resume_choice.data == 'profile':
            if user.seeker_profile and user.seeker_profile.resume_filename:
                resume_filename = user.seeker_profile.resume_filename
            else:
                flash('You do not have a resume uploaded in your profile. Please upload a PDF resume below.', 'danger')
                return redirect(url_for('jobs.details', job_id=job.id))
        else:
            if not form.resume_file.data:
                flash('Please select a PDF file to upload as your resume.', 'danger')
                return redirect(url_for('jobs.details', job_id=job.id))
            try:
                resume_filename = save_resume(form.resume_file.data, user.id)
            except ValueError as e:
                flash(str(e), 'danger')
                return redirect(url_for('jobs.details', job_id=job.id))

        new_application = Application(
            job_id=job.id,
            job_seeker_id=user.id,
            resume_filename=resume_filename,
            cover_letter=form.cover_letter.data.strip() if form.cover_letter.data else None,
            application_status='Under Review'
        )

        db.session.add(new_application)
        db.session.commit()

        log_activity(
            user.id, 
            'APPLICATION_SUBMITTED', 
            f"Applied for '{job.job_title}' at {job.company.company_name}"
        )

        flash(f'Congratulations! Your application for {job.job_title} has been successfully submitted.', 'success')
        return redirect(url_for('seeker.dashboard'))

    flash('Failed to submit application. Please check your submission and try again.', 'danger')
    return redirect(url_for('jobs.details', job_id=job.id))


@jobs_bp.route('/jobs/new', methods=['GET', 'POST'])
@login_required
@role_required('employer')
def post_job():
    user = get_current_user()
    company = user.company
    if not company or not company.company_name:
        flash('Please complete your company profile before posting a job vacancy.', 'warning')
        return redirect(url_for('employer.company_profile'))

    form = JobForm()
    if form.validate_on_submit():
        new_job = Job(
            employer_id=user.id,
            company_id=company.id,
            job_title=form.job_title.data.strip(),
            category=form.category.data,
            employment_type=form.employment_type.data,
            location=form.location.data.strip(),
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            required_skills=form.required_skills.data.strip(),
            qualifications=form.qualifications.data.strip(),
            job_description=form.job_description.data.strip(),
            application_deadline=form.application_deadline.data,
            status=form.status.data,
            is_featured=form.is_featured.data
        )

        db.session.add(new_job)
        db.session.commit()

        log_activity(user.id, 'JOB_POSTED', f"Posted new job: '{new_job.job_title}'")
        flash(f'Job vacancy "{new_job.job_title}" has been published successfully!', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('jobs/post.html', form=form, title='Post a New Vacancy')


@jobs_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)

    user = get_current_user()
    if not (user.is_admin or (user.is_employer and job.employer_id == user.id)):
        abort(403)

    form = JobForm(obj=job)
    if form.validate_on_submit():
        job.job_title = form.job_title.data.strip()
        job.category = form.category.data
        job.employment_type = form.employment_type.data
        job.location = form.location.data.strip()
        job.salary_min = form.salary_min.data
        job.salary_max = form.salary_max.data
        job.required_skills = form.required_skills.data.strip()
        job.qualifications = form.qualifications.data.strip()
        job.job_description = form.job_description.data.strip()
        job.application_deadline = form.application_deadline.data
        job.status = form.status.data
        job.is_featured = form.is_featured.data

        db.session.commit()
        log_activity(user.id, 'JOB_UPDATED', f"Updated job listing: '{job.job_title}'")
        flash(f'Job listing "{job.job_title}" updated successfully!', 'success')

        if user.is_admin:
            return redirect(url_for('admin.jobs'))
        return redirect(url_for('employer.dashboard'))

    return render_template('jobs/edit.html', form=form, job=job, title='Edit Job Listing')


@jobs_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)

    user = get_current_user()
    if not (user.is_admin or (user.is_employer and job.employer_id == user.id)):
        abort(403)

    title = job.job_title
    db.session.delete(job)
    db.session.commit()

    log_activity(user.id, 'JOB_DELETED', f"Deleted job vacancy: '{title}'")
    flash(f'Job listing "{title}" was removed.', 'info')

    if user.is_admin:
        return redirect(url_for('admin.jobs'))
    return redirect(url_for('employer.dashboard'))


@jobs_bp.route('/jobs/<int:job_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)

    user = get_current_user()
    if not (user.is_admin or (user.is_employer and job.employer_id == user.id)):
        abort(403)

    job.status = 'Closed' if job.status == 'Active' else 'Active'
    db.session.commit()

    flash(f'Job listing status changed to {job.status}.', 'success')
    if user.is_admin:
        return redirect(url_for('admin.jobs'))
    return redirect(url_for('employer.dashboard'))
