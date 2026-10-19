from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from sqlalchemy import func
from models import db, User, Job, Company, Application, PlatformActivity, JobSeekerProfile
from utils import get_current_user, login_required, role_required, log_activity

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
@role_required('admin')
def require_admin():
    """Ensure every route in this blueprint is restricted strictly to administrators"""
    pass

@admin_bp.route('/admin')
def dashboard():
    total_users = User.query.count()
    total_employers = User.query.filter_by(role='employer').count()
    total_seekers = User.query.filter_by(role='job_seeker').count()
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(status='Active').count()
    closed_jobs = Job.query.filter_by(status='Closed').count()
    total_applications = Application.query.count()

    # Application statuses breakdown
    status_counts = db.session.query(
        Application.application_status, func.count(Application.id)
    ).group_by(Application.application_status).all()
    status_dict = dict(status_counts)

    # Categories breakdown
    cat_counts = db.session.query(
        Job.category, func.count(Job.id)
    ).group_by(Job.category).all()
    categories_list = [c[0] for c in cat_counts]
    categories_counts = [c[1] for c in cat_counts]

    # Recent platform activities
    activities = PlatformActivity.query.order_by(PlatformActivity.created_at.desc()).limit(20).all()

    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    # Recent job postings
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_employers=total_employers,
        total_seekers=total_seekers,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        closed_jobs=closed_jobs,
        total_applications=total_applications,
        status_dict=status_dict,
        categories_list=categories_list,
        categories_counts=categories_counts,
        activities=activities,
        recent_users=recent_users,
        recent_jobs=recent_jobs
    )


@admin_bp.route('/admin/users')
def users():
    role_filter = request.args.get('role', '').strip()
    q = request.args.get('q', '').strip()

    query = User.query

    if role_filter and role_filter != 'All':
        query = query.filter_by(role=role_filter)

    if q:
        query = query.filter(
            (User.full_name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
        )

    users_list = query.order_by(User.created_at.desc()).all()

    return render_template(
        'admin/users.html',
        users=users_list,
        role_filter=role_filter,
        q=q
    )


@admin_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    current_admin = get_current_user()
    if current_admin.id == user_id:
        flash('You cannot deactivate your own administrative account.', 'warning')
        return redirect(url_for('admin.users'))

    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    user.is_active = not user.is_active
    db.session.commit()

    action_text = "activated" if user.is_active else "deactivated"
    log_activity(current_admin.id, 'ADMIN_ACTION', f"Admin {action_text} user account: {user.email}")
    flash(f"Account for {user.full_name} has been {action_text}.", 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    current_admin = get_current_user()
    if current_admin.id == user_id:
        flash('You cannot delete your own administrative account.', 'warning')
        return redirect(url_for('admin.users'))

    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    email = user.email
    db.session.delete(user)
    db.session.commit()

    log_activity(current_admin.id, 'ADMIN_ACTION', f"Admin deleted user: {email}")
    flash(f"User {email} has been permanently deleted.", 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/jobs')
def jobs():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()

    query = Job.query

    if q:
        query = query.join(Company).filter(
            (Job.job_title.ilike(f"%{q}%")) | (Company.company_name.ilike(f"%{q}%"))
        )

    if category and category != 'All':
        query = query.filter(Job.category == category)

    if status and status != 'All':
        query = query.filter(Job.status == status)

    jobs_list = query.order_by(Job.created_at.desc()).all()

    return render_template(
        'admin/jobs.html',
        jobs=jobs_list,
        q=q,
        category=category,
        status=status
    )


@admin_bp.route('/admin/jobs/<int:job_id>/toggle-featured', methods=['POST'])
def toggle_featured(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)

    job.is_featured = not job.is_featured
    db.session.commit()

    feat_text = "featured on homepage" if job.is_featured else "unfeatured"
    flash(f"Job '{job.job_title}' is now {feat_text}.", 'success')
    return redirect(url_for('admin.jobs'))


@admin_bp.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    current_admin = get_current_user()
    job = db.session.get(Job, job_id)
    if not job:
        abort(404)

    title = job.job_title
    db.session.delete(job)
    db.session.commit()

    log_activity(current_admin.id, 'ADMIN_ACTION', f"Admin removed job vacancy: {title}")
    flash(f"Job vacancy '{title}' has been removed.", 'info')
    return redirect(url_for('admin.jobs'))
