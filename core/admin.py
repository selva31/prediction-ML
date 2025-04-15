from flask import Blueprint, render_template
from flask_login import login_required
from core.models import User

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()  # Fetch all users
    return render_template('admin/dashboard.html', users=users)
