from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# Create Blueprint for main app
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')  # Your homepage template


