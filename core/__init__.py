from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

# Initialize Migrate (this will be inside the create_app function)
migrate = Migrate()

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
    migrate.init_app(app, db)  # This should be initialized after the app


    # Import and register Blueprints
    from core.auth import auth_bp
    from core.student import student_bp
    from core.teacher import teacher_bp
    from core.admin import admin_bp
    from core.main import main_bp  # Correctly import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')  # Corrected the URL prefix
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Corrected the URL prefix
    app.register_blueprint(main_bp)  # Register main_bp blueprint

    return app
