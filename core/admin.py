from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user
from werkzeug.security import generate_password_hash
from core.models import User, Performance
from core import db
from core.forms import AddStudentForm, AddTeacherForm, LoginForm, SearchForm
from flask_login import current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates/admin')

def create_admin():
    if not User.query.filter_by(email='admin17@gmail.com').first():
        admin = User(
            username='admin',
            email='admin17@gmail.com',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='Admin'
        )
        db.session.add(admin)
        db.session.commit()


# Admin Login
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(email=form.email.data, role='Admin').first()
        if admin and admin.check_password(form.password.data):  # Password check using check_password method
            login_user(admin)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('admin/login.html', form=form)

# Admin Dashboard
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'Admin':
        return redirect(url_for('main.home'))

    total_students = User.query.filter_by(role='Student').count()
    total_teachers = User.query.filter_by(role='Teacher').count()
    total_performance_records = Performance.query.count()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_performance_records=total_performance_records
    )


# Add Student
@admin_bp.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    form = AddStudentForm()

    if form.validate_on_submit():
        new_student = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role='Student',
            roll_no=form.roll_no.data,
            phone=form.phone.data
        )
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('admin.view_student'))

    return render_template('admin/add_student.html', form=form)


# Add Teacher
@admin_bp.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = AddTeacherForm()

    if form.validate_on_submit():
        # Create new teacher instance
        new_teacher = User(
            username=form.username.data,  # Use 'username' here for the teacher's name
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role='Teacher'  # Ensure role is set to 'Teacher'
        )

        # Add the teacher to the database
        db.session.add(new_teacher)
        db.session.commit()

        flash(f'Teacher {new_teacher.username} added successfully!', 'success')
        return redirect(url_for('admin.view_teacher'))  # Redirect to view_teacher page

    return render_template('admin/add_teacher.html', form=form)

#view teacher
@admin_bp.route('/view_teacher', methods=['GET'])
@login_required
def view_teacher():
    teachers = User.query.filter_by(role='Teacher').all()  # Fetch all teachers
    return render_template('admin/view_teacher.html', teachers=teachers)

@admin_bp.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)

    if request.method == 'POST':
        teacher.username = request.form['username']
        teacher.email = request.form['email']
        db.session.commit()
        flash("Teacher updated successfully", "success")
        return redirect(url_for('admin.view_teacher'))

    return render_template('admin/edit_teacher.html', teacher=teacher)




@admin_bp.route('/delete_teacher/<int:teacher_id>')
def delete_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully.', 'success')
    return redirect(url_for('admin.view_teacher'))


# View Students
@admin_bp.route('/admin/view_student', methods=['GET', 'POST'])
def view_student():
    form = SearchForm()
    students = User.query.filter_by(role='Student').all()

    if form.validate_on_submit():  # If the search query is submitted
        search_query = form.search_query.data
        students = User.query.filter(User.username.like(f'%{search_query}%')).all()

    return render_template('admin/view_student.html', students=students, form=form)


# Edit Student
@admin_bp.route('/admin/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = User.query.get_or_404(student_id)
    if request.method == 'POST':
        student.username = request.form['username']
        student.email = request.form['email']
        student.roll_no = request.form['roll_no']
        student.phone = request.form['phone']

        try:
            db.session.commit()
            flash('Student details updated successfully!', 'success')
            return redirect(url_for('admin.view_student'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating student: ' + str(e), 'danger')
            return redirect(url_for('admin.view_student'))
    return render_template('admin/edit_student.html', student=student)


# Delete Student
@admin_bp.route('/delete_student/<int:student_id>', methods=['GET'])
@login_required
def delete_student(student_id):
    if current_user.role != 'Admin':
        return redirect(url_for('main.home'))  # Redirect non-admins

    student = User.query.get_or_404(student_id)

    # First delete associated performance records
    from core.models import PerformanceRecord, Performance, StudentDetail

    PerformanceRecord.query.filter_by(student_id=student.id).delete()
    Performance.query.filter_by(student_id=student.id).delete()
    StudentDetail.query.filter_by(user_id=student.id).delete()

    # Now delete the student
    db.session.delete(student)
    db.session.commit()

    flash('Student detail  deleted successfully.')
    return redirect(url_for('admin.view_student'))


# View Performance
@admin_bp.route('/view_performance')
@login_required
def view_performance():
    if current_user.role != 'Admin':
        return redirect(url_for('main.home'))  # Redirect non-admins

    performance_records = Performance.query.all()
    return render_template('admin/view_performance.html', performance_records=performance_records)

# Search Students
@admin_bp.route('/admin/search_student', methods=['POST'])
def search_students():
    form = SearchForm()
    query = form.search_query.data
    students = User.query.filter(User.role == 'Student', User.username.contains(query)).all()
    return render_template('admin/view_student.html', students=students, form=form)

