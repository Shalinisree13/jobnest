import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jobnest-super-secret-key-2026-production-ready')
    
    # SQLite Database location in instance/ folder
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        /"sqlite:///{os.path.join(INSTANCE_DIR, 'jobnest.db').replace('\\', '/')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'resumes')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Megabytes limit
    ALLOWED_EXTENSIONS = {'pdf'}

    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
