import os
from datetime import datetime, timezone, date
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import db, User
from utils import get_current_user

# Import blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.jobs import jobs_bp
from routes.seeker import seeker_bp
from routes.employer import employer_bp
from routes.admin import admin_bp

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(seeker_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)

    # Context processor to make current_user and helper values available in all Jinja templates
    @app.context_processor
    def inject_context():
        user = get_current_user()
        return dict(
            current_user=user,
            now=datetime.now(timezone.utc),
            current_year=datetime.now(timezone.utc).year
        )

    # Custom Jinja template filters
    @app.template_filter('timeago')
    def timeago_filter(dt):
        if not dt:
            return ''
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())

        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} min ago" if minutes == 1 else f"{minutes} mins ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days} day ago" if days == 1 else f"{days} days ago"
        else:
            return dt.strftime('%b %d, %Y')

    @app.template_filter('format_date')
    def format_date_filter(val):
        if not val:
            return 'N/A'
        if isinstance(val, date) or isinstance(val, datetime):
            return val.strftime('%b %d, %Y')
        return str(val)

    @app.template_filter('status_badge_class')
    def status_badge_class(status):
        mapping = {
            'Under Review': 'badge-warning',
            'Pending': 'badge-warning',
            'Shortlisted': 'badge-info',
            'Interview Scheduled': 'badge-primary',
            'Hired': 'badge-success',
            'Rejected': 'badge-danger',
            'Withdrawn': 'badge-secondary',
            'Active': 'badge-success',
            'Closed': 'badge-secondary'
        }
        return mapping.get(status, 'badge-secondary')

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html', description=getattr(error, 'description', None)), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # CLI command to initialize database tables
    @app.cli.command('init-db')
    def init_db_command():
        with app.app_context():
            db.create_all()
            print("Database initialized successfully.")

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
