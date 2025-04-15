from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from core.models import User
from core import db, login_manager

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'Student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'Teacher':
                return redirect(url_for('teacher.dashboard'))
            elif user.role == 'Admin':
                return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials')
    return render_template('auth/login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        password = generate_password_hash(request.form['password'], method='sha256')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists')
        else:
            new_user = User(username=username, email=email, role=role, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please log in.')
            return redirect(url_for('auth.login'))
    return render_template('auth/signup.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
