from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

# Configure login redirection
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)

    # App Configs
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'santhoshkumar@gmail.com'  # Replace with your email
    app.config['MAIL_PASSWORD'] = 'password'  # Replace with your app password

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Import and register Blueprints
    from .auth import auth_bp
    from .student import student_bp
    from .teacher import teacher_bp
    from .admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)

    return app
