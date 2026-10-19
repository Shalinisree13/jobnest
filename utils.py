import os
import uuid
from functools import wraps
from flask import session, redirect, url_for, flash, request, g, current_app, abort
from werkzeug.utils import secure_filename
from models import User, PlatformActivity, db

def get_current_user():
    """Retrieve current logged in user and cache in flask.g for request lifecycle"""
    user_id = session.get('user_id')
    if not user_id:
        g.current_user = None
        return None
    if getattr(g, 'current_user', None) is None or getattr(g.current_user, 'id', None) != user_id:
        g.current_user = db.session.get(User, user_id)
    return g.current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_active:
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user or not user.is_active:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            if user.role not in roles:
                flash('You do not have permission to access that resource.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def is_valid_pdf(file_storage):
    """Validate that the file has a .pdf extension and valid PDF header magic bytes"""
    if not file_storage or not file_storage.filename:
        return False
    
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    if ext != 'pdf':
        return False

    # Check magic bytes for PDF (%PDF-)
    pos = file_storage.tell()
    file_storage.seek(0)
    header = file_storage.read(5)
    file_storage.seek(pos)
    
    return header.startswith(b'%PDF')

def save_resume(file_storage, user_id):
    """Save an uploaded PDF resume safely and return the stored filename"""
    if not is_valid_pdf(file_storage):
        raise ValueError("Invalid file format. Only legitimate PDF documents are accepted.")
    
    original_name = secure_filename(file_storage.filename)
    if not original_name:
        original_name = "resume.pdf"
    
    unique_prefix = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
    filename = f"{unique_prefix}_{original_name}"
    
    upload_path = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_path, exist_ok=True)
    destination = os.path.join(upload_path, filename)
    file_storage.save(destination)
    return filename

def log_activity(user_id, action, description):
    """Record an audit trail activity in the database"""
    try:
        activity = PlatformActivity(user_id=user_id, action=action, description=description)
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f"Failed to log activity: {e}")
