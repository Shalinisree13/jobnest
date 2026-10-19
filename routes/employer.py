from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from models import db, Job, Company, Application, User, JobSeekerProfile
from forms import CompanyProfileForm, StatusUpdateForm
from utils import get_current_user, login_required, role_required, log_activity

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/employer/dashboard')
@login_required
@role_required('employer')
def dashboard():
    user = get_current_user()
    company = user.company
    if not company:
        company = Company(employer_id=user.id, company_name=f"{user.full_name}'s Enterprise")
        db.session.add(company)
        db.session.commit()

    # Jobs posted by this employer
    jobs = Job.query.filter_by(employer_id=user.id).order_by(Job.created_at.desc()).all()
    job_ids = [j.id for j in jobs]

    # Applications for employer's jobs
    if job_ids:
        applications = Application.query.filter(Application.job_id.in_(job_ids))\
            .order_by(Application.applied_at.desc()).all()
    else:
        applications = []

    total_jobs = len(jobs)
    active_jobs = sum(1 for j in jobs if j.status == 'Active')
    total_applications = len(applications)
    under_review_count = sum(1 for a in applications if a.application_status == 'Under Review')
    shortlisted_count = sum(1 for a in applications if a.application_status == 'Shortlisted')
    interview_count = sum(1 for a in applications if a.application_status == 'Interview Scheduled')
    hired_count = sum(1 for a in applications if a.application_status == 'Hired')

    return render_template(
        'employer/dashboard.html',
        user=user,
        company=company,
        jobs=jobs,
        applications=applications[:10],  # Recent 10 applications
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_applications=total_applications,
        under_review_count=under_review_count,
        shortlisted_count=shortlisted_count,
        interview_count=interview_count,
        hired_count=hired_count
    )


@employer_bp.route('/employer/company', methods=['GET', 'POST'])
@login_required
@role_required('employer')
def company_profile():
    user = get_current_user()
    company = user.company
    if not company:
        company = Company(employer_id=user.id, company_name=f"{user.full_name}'s Company")
        db.session.add(company)
        db.session.commit()

    form = CompanyProfileForm()

    if request.method == 'GET':
        form.company_name.data = company.company_name
        form.company_website.data = company.company_website
        form.location.data = company.location
        form.industry.data = company.industry
        form.company_description.data = company.company_description

    if form.validate_on_submit():
        company.company_name = form.company_name.data.strip()
        company.company_website = form.company_website.data.strip() if form.company_website.data else None
        company.location = form.location.data.strip()
        company.industry = form.industry.data
        company.company_description = form.company_description.data.strip()

        db.session.commit()
        log_activity(user.id, 'COMPANY_UPDATED', f"Updated company profile for {company.company_name}")
        flash('Company profile updated successfully!', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/company.html', form=form, company=company)


@employer_bp.route('/employer/jobs/<int:job_id>/applicants')
@login_required
@role_required('employer')
def applicants(job_id):
    user = get_current_user()
    job = db.session.get(Job, job_id)
    if not job or job.employer_id != user.id:
        abort(403)

    status_filter = request.args.get('status', '').strip()
    query = Application.query.filter_by(job_id=job.id)

    if status_filter and status_filter != 'All':
        query = query.filter_by(application_status=status_filter)

    applications = query.order_by(Application.applied_at.desc()).all()
    status_form = StatusUpdateForm()

    return render_template(
        'employer/applicants.html',
        job=job,
        applications=applications,
        status_filter=status_filter,
        status_form=status_form
    )


@employer_bp.route('/employer/applications/<int:app_id>/status', methods=['POST'])
@login_required
@role_required('employer')
def update_application_status(app_id):
    user = get_current_user()
    application = db.session.get(Application, app_id)
    if not application:
        abort(404)

    if application.job.employer_id != user.id:
        abort(403)

    new_status = request.form.get('application_status')
    valid_statuses = ['Under Review', 'Shortlisted', 'Interview Scheduled', 'Hired', 'Rejected']

    if new_status in valid_statuses:
        old_status = application.application_status
        application.application_status = new_status
        db.session.commit()

        log_activity(
            user.id, 
            'STATUS_CHANGE', 
            f"Changed application status for {application.applicant.full_name} to '{new_status}' on job '{application.job.job_title}'"
        )
        flash(f"Status for {application.applicant.full_name} updated to {new_status}.", 'success')
    else:
        flash("Invalid status selected.", 'danger')

    # Return back to applicants page or dashboard
    return redirect(request.referrer or url_for('employer.dashboard'))
