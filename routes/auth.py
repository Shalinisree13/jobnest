from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User, JobSeekerProfile, Company
from forms import RegistrationForm, LoginForm
from utils import get_current_user, log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    if user:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing_user:
            flash('An account with this email address already exists. Please log in.', 'danger')
            return render_template('auth/register.html', form=form)

        new_user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            role=form.role.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.flush()  # to obtain new_user.id

        if new_user.role == 'job_seeker':
            profile = JobSeekerProfile(user_id=new_user.id)
            db.session.add(profile)
        elif new_user.role == 'employer':
            company = Company(
                employer_id=new_user.id,
                company_name=f"{new_user.full_name}'s Organization"
            )
            db.session.add(company)

        db.session.commit()
        log_activity(new_user.id, 'REGISTER', f"User {new_user.full_name} registered as {new_user.role}")

        # Automatically log the user in
        session['user_id'] = new_user.id
        session['user_role'] = new_user.role
        session['user_name'] = new_user.full_name

        flash(f'Welcome to JobNest, {new_user.full_name}! Your account has been created.', 'success')

        if new_user.is_seeker:
            return redirect(url_for('seeker.profile'))
        elif new_user.is_employer:
            return redirect(url_for('employer.company_profile'))
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if user:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html', form=form)

            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.full_name
            session.permanent = form.remember.data

            log_activity(user.id, 'LOGIN', f"User {user.email} signed in")
            flash(f'Welcome back, {user.full_name}!', 'success')

            next_page = request.args.get('next')
            if next_page and not next_page.startswith('//') and not next_page.startswith('http'):
                return redirect(next_page)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_employer:
                return redirect(url_for('employer.dashboard'))
            else:
                return redirect(url_for('seeker.dashboard'))
        else:
            flash('Invalid email or password. Please check your credentials.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        log_activity(user_id, 'LOGOUT', "User signed out")
    session.clear()
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('main.index'))
