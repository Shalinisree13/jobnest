from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from models import db, Application, Job, JobSeekerProfile, User
from forms import JobSeekerProfileForm
from utils import get_current_user, login_required, role_required, save_resume, log_activity

seeker_bp = Blueprint('seeker', __name__)

@seeker_bp.route('/seeker/dashboard')
@login_required
@role_required('job_seeker')
def dashboard():
    user = get_current_user()
    profile = user.seeker_profile
    if not profile:
        profile = JobSeekerProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    completion_pct = profile.calculate_completion()

    # User's applications
    applications = Application.query.filter_by(job_seeker_id=user.id)\
        .order_by(Application.applied_at.desc()).all()

    total_applied = len(applications)
    under_review = sum(1 for a in applications if a.application_status == 'Under Review')
    shortlisted = sum(1 for a in applications if a.application_status == 'Shortlisted')
    interview_scheduled = sum(1 for a in applications if a.application_status == 'Interview Scheduled')
    hired = sum(1 for a in applications if a.application_status == 'Hired')
    rejected = sum(1 for a in applications if a.application_status == 'Rejected')

    # Job recommendations based on seeker skills
    applied_job_ids = [a.job_id for a in applications]
    user_skills = [s.lower() for s in profile.get_skills_list()]
    
    # Base recommendations query: active jobs seeker hasn't applied to yet
    rec_query = Job.query.filter(
        Job.status == 'Active',
        ~Job.id.in_(applied_job_ids if applied_job_ids else [-1])
    )
    
    recommended_jobs = []
    all_active = rec_query.limit(20).all()
    if user_skills:
        # Score jobs by matching skills
        scored_jobs = []
        for j in all_active:
            score = sum(1 for sk in user_skills if sk in (j.required_skills or '').lower() or sk in j.job_title.lower())
            scored_jobs.append((score, j))
        scored_jobs.sort(key=lambda x: x[0], reverse=True)
        recommended_jobs = [j for score, j in scored_jobs[:4]]
    else:
        recommended_jobs = all_active[:4]

    return render_template(
        'seeker/dashboard.html',
        user=user,
        profile=profile,
        completion_pct=completion_pct,
        applications=applications,
        total_applied=total_applied,
        under_review=under_review,
        shortlisted=shortlisted,
        interview_scheduled=interview_scheduled,
        hired=hired,
        rejected=rejected,
        recommended_jobs=recommended_jobs
    )


@seeker_bp.route('/seeker/profile', methods=['GET', 'POST'])
@login_required
@role_required('job_seeker')
def profile():
    user = get_current_user()
    profile = user.seeker_profile
    if not profile:
        profile = JobSeekerProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    form = JobSeekerProfileForm()

    if request.method == 'GET':
        form.full_name.data = user.full_name
        form.phone.data = profile.phone
        form.location.data = profile.location
        form.headline.data = profile.headline
        form.skills.data = profile.skills
        form.experience.data = profile.experience
        form.education.data = profile.education

    if form.validate_on_submit():
        user.full_name = form.full_name.data.strip()
        profile.phone = form.phone.data.strip() if form.phone.data else None
        profile.location = form.location.data.strip() if form.location.data else None
        profile.headline = form.headline.data.strip() if form.headline.data else None
        profile.skills = form.skills.data.strip() if form.skills.data else None
        profile.experience = form.experience.data.strip() if form.experience.data else None
        profile.education = form.education.data.strip() if form.education.data else None

        # Check for uploaded resume
        if form.resume.data:
            try:
                saved_filename = save_resume(form.resume.data, user.id)
                profile.resume_filename = saved_filename
                flash('Resume uploaded and verified successfully!', 'info')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('seeker/profile.html', form=form, profile=profile)

        db.session.commit()
        log_activity(user.id, 'PROFILE_UPDATED', "Updated job seeker profile")
        flash('Your profile has been saved successfully!', 'success')
        return redirect(url_for('seeker.dashboard'))

    return render_template('seeker/profile.html', form=form, profile=profile)


@seeker_bp.route('/seeker/applications/<int:app_id>/withdraw', methods=['POST'])
@login_required
@role_required('job_seeker')
def withdraw_application(app_id):
    user = get_current_user()
    application = db.session.get(Application, app_id)
    if not application:
        abort(404)

    if application.job_seeker_id != user.id:
        abort(403)

    if application.application_status in ['Hired', 'Withdrawn']:
        flash(f'Cannot withdraw an application with status "{application.application_status}".', 'warning')
        return redirect(url_for('seeker.dashboard'))

    application.application_status = 'Withdrawn'
    db.session.commit()

    log_activity(user.id, 'APPLICATION_WITHDRAWN', f"Withdrew application for job '{application.job.job_title}'")
    flash('Your application has been withdrawn.', 'info')
    return redirect(url_for('seeker.dashboard'))
