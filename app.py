from flask import Flask, render_template, request, session
import mysql.connector
from flask import redirect, url_for
import os
from flask import send_from_directory
from flask_mail import Mail, Message
import random
from flask import flash, redirect, url_for

app = Flask(__name__)
app.secret_key = "placement_secret"

app.config['UPLOAD_FOLDER'] = 'uploads'
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="placement_management_system"
)
app.secret_key = "placement_secret_key"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jaykoladiya2409@gmail.com'
app.config['MAIL_PASSWORD'] = 'znck zcrm skqg niop'

mail = Mail(app)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        department = request.form['department']
        cgpa = request.form['cgpa']

        sql = """
        INSERT INTO students
        (full_name,email,password,phone,department,cgpa)
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        values = (
            full_name,
            email,
            password,
            phone,
            department,
            cgpa
        )

        cursor.execute(sql, values)
        db.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = """
        SELECT *
        FROM students
        WHERE email=%s
        AND password=%s
        """

        cursor.execute(sql, (email, password))

        student = cursor.fetchone()

        if student:

            session['student_id'] = student[0]

            return redirect('/dashboard')

        else:

            return "Invalid Email or Password"

    return render_template('login.html')


@app.route('/profile')
def profile():

    student_id = session.get('student_id')

    sql = "SELECT * FROM students WHERE id=%s"

    cursor.execute(sql, (student_id,))

    student = cursor.fetchone()

    return render_template(
        'profile.html',
        student=student
    )

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/jobs')
def jobs():

    search = request.args.get('search')

    if search:

        sql = """
        SELECT *
        FROM jobs
        WHERE company_name LIKE %s
        OR job_role LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(
            sql,
            (value, value)
        )

    else:

        cursor.execute(
            "SELECT * FROM jobs"
        )

    jobs = cursor.fetchall()

    return render_template(
        'jobs.html',
        jobs=jobs
    )

@app.route('/apply/<int:job_id>')
def apply(job_id):

    student_id = session.get('student_id')

    sql = """
    INSERT INTO applications
    (student_id, job_id, status)
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        sql,
        (student_id, job_id, 'Applied')
    )

    db.commit()

    return "Job Applied Successfully"

@app.route('/applications')
def applications():

    student_id = session.get('student_id')

    sql = """
    SELECT jobs.company_name,
           jobs.job_role,
           applications.status
    FROM applications
    JOIN jobs
    ON applications.job_id = jobs.id
    WHERE applications.student_id = %s
    """

    cursor.execute(sql, (student_id,))

    applications = cursor.fetchall()

    return render_template(
        'applications.html',
        applications=applications
    )

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        sql = """
        SELECT *
        FROM admin
        WHERE username=%s
        AND password=%s
        """

        cursor.execute(
            sql,
            (username, password)
        )

        admin = cursor.fetchone()

        if admin:
            session['admin'] = username
            return redirect('/admin-dashboard')
            

        return "Invalid Admin Login"

    return render_template(
        'admin_login.html'
    )
@app.route('/admin-dashboard')
def admin_dashboard():

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications")
    total_applications = cursor.fetchone()[0]

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_jobs=total_jobs,
        total_applications=total_applications
    )

@app.route('/admin-jobs')
def admin_jobs():

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    return render_template(
        'admin_jobs.html',
        jobs=jobs
    )

@app.route('/all-students')
def all_students():

    search = request.args.get('search')

    if search:

        sql = """
        SELECT *
        FROM students
        WHERE full_name LIKE %s
        OR email LIKE %s
        OR department LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(
            sql,
            (value, value, value)
        )

    else:

        cursor.execute(
            "SELECT * FROM students"
        )

    students = cursor.fetchall()

    return render_template(
        'all_students.html',
        students=students
    )

@app.route('/all-applications')
def all_applications():

    sql = """
    SELECT applications.student_id,
           jobs.company_name,
           jobs.job_role,
           applications.status
    FROM applications
    JOIN jobs
    ON applications.job_id = jobs.id
    """

    cursor.execute(sql)

    applications = cursor.fetchall()

    return render_template(
        'all_applications.html',
        applications=applications
    )

@app.route('/shortlist/<int:student_id>')
def shortlist(student_id):

    sql = """
    UPDATE applications
    SET status='Shortlisted'
    WHERE student_id=%s
    """

    cursor.execute(sql, (student_id,))

    db.commit()

    return "Student Shortlisted Successfully"
    
@app.route('/add-job', methods=['GET', 'POST'])
def add_job():

    if request.method == 'POST':

        company_name = request.form['company_name']
        job_role = request.form['job_role']
        package_lpa = request.form['package_lpa']
        eligibility_cgpa = request.form['eligibility_cgpa']
        deadline = request.form['deadline']

        sql = """
        INSERT INTO jobs
        (company_name, job_role,
         package_lpa,
         eligibility_cgpa,
         deadline)
        VALUES (%s,%s,%s,%s,%s)
        """

        cursor.execute(
            sql,
            (
                company_name,
                job_role,
                package_lpa,
                eligibility_cgpa,
                deadline
            )
        )

        db.commit()

        flash(
            "✅ Job Added Successfully",
            "success"
        )

        return redirect(url_for('add_job'))

    return render_template('add_job.html')
    
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

@app.route('/upload-resume', methods=['POST'])
def upload_resume():

    file = request.files['resume']

    filename = file.filename

    file.save(
        os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )
    )

    student_id = session.get('student_id')

    sql = """
    UPDATE students
    SET resume=%s
    WHERE id=%s
    """

    cursor.execute(
        sql,
        (filename, student_id)
    )

    db.commit()

    return "Resume Uploaded Successfully"

@app.route('/resume/<filename>')
def resume(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )

@app.route('/delete-job/<int:job_id>')
def delete_job(job_id):

    cursor.execute(
        "DELETE FROM jobs WHERE id=%s",
        (job_id,)
    )

    db.commit()

    return redirect('/admin-jobs')

@app.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):

    if request.method == 'POST':

        company_name = request.form['company_name']
        job_role = request.form['job_role']
        package_lpa = request.form['package_lpa']
        eligibility_cgpa = request.form['eligibility_cgpa']
        deadline = request.form['deadline']

        sql = """
        UPDATE jobs
        SET company_name=%s,
            job_role=%s,
            package_lpa=%s,
            eligibility_cgpa=%s,
            deadline=%s
        WHERE id=%s
        """

        cursor.execute(
            sql,
            (
                company_name,
                job_role,
                package_lpa,
                eligibility_cgpa,
                deadline,
                job_id
            )
        )

        db.commit()

        return redirect('/admin-jobs')

    cursor.execute(
        "SELECT * FROM jobs WHERE id=%s",
        (job_id,)
    )

    job = cursor.fetchone()

    return render_template(
        'edit_job.html',
        job=job
    )
@app.route('/placement-report')
def placement_report():

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications")
    total_applications = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE status='Selected'"
    )
    selected_students = cursor.fetchone()[0]

    if total_students > 0:
        placement_percentage = (
            selected_students / total_students
        ) * 100
    else:
        placement_percentage = 0

    # Chart Data
    cursor.execute("""
        SELECT status,
               COUNT(*)
        FROM applications
        GROUP BY status
    """)

    status_data = cursor.fetchall()

    return render_template(
        'placement_report.html',
        total_students=total_students,
        total_jobs=total_jobs,
        total_applications=total_applications,
        selected_students=selected_students,
        placement_percentage=placement_percentage,
        status_data=status_data
    )

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():

    student_id = session.get('student_id')

    if request.method == 'POST':

        phone = request.form['phone']
        department = request.form['department']
        cgpa = request.form['cgpa']

        sql = """
        UPDATE students
        SET phone=%s,
            department=%s,
            cgpa=%s
        WHERE id=%s
        """

        cursor.execute(
            sql,
            (
                phone,
                department,
                cgpa,
                student_id
            )
        )

        db.commit()

        return redirect('/profile')

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (student_id,)
    )

    student = cursor.fetchone()

    return render_template(
        'edit_profile.html',
        student=student
    )

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():

    student_id = session.get('student_id')

    if request.method == 'POST':

        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cursor.execute(
            "SELECT password FROM students WHERE id=%s",
            (student_id,)
        )

        current_password = cursor.fetchone()[0]

        if old_password != current_password:

            flash("❌ Old Password Incorrect", "danger")
            return redirect(url_for('change_password'))

        if new_password != confirm_password:

            flash("❌ New Passwords Do Not Match", "danger")
            return redirect(url_for('change_password'))

        cursor.execute(
            "UPDATE students SET password=%s WHERE id=%s",
            (new_password, student_id)
        )

        db.commit()

        flash("✅ Password Changed Successfully", "success")
        return redirect(url_for('change_password'))

    return render_template(
        'change_password.html'
    )


@app.route('/schedule-interview', methods=['GET', 'POST'])
def schedule_interview():

    if request.method == 'POST':

        student_id = request.form['student_id']
        company_name = request.form['company_name']
        interview_date = request.form['interview_date']
        interview_time = request.form['interview_time']

        # Insert Interview
        cursor.execute(
            """
            INSERT INTO interviews
            (student_id, company_name,
             interview_date, interview_time)
            VALUES (%s,%s,%s,%s)
            """,
            (
                student_id,
                company_name,
                interview_date,
                interview_time
            )
        )

        # Insert Notification
        message = (
            f"Interview scheduled with {company_name} "
            f"on {interview_date} at {interview_time}"
        )

        cursor.execute(
            """
            INSERT INTO notifications
            (student_id, message)
            VALUES (%s,%s)
            """,
            (
                student_id,
                message
            )
        )

        db.commit()

        # Get Student Email
        cursor.execute(
            "SELECT email FROM students WHERE id=%s",
            (student_id,)
        )

        student = cursor.fetchone()

        student_email = student[0]

        # Send Email
        msg = Message(
            'Interview Scheduled',
            sender='yourgmail@gmail.com',
            recipients=[student_email]
        )

        msg.body = f"""
Dear Student,

Your interview with {company_name} has been scheduled.

Date: {interview_date}
Time: {interview_time}

Best of Luck!

GTU-ITR PMS
"""

        mail.send(msg)

        flash(
    "✅ Interview Scheduled Successfully",
    "success"
)

        return redirect(url_for('schedule_interview'))

    return render_template('schedule_interview.html')
@app.route('/my-interviews')
def my_interviews():

    student_id = session.get('student_id')

    cursor.execute(
        """
        SELECT company_name,
               interview_date,
               interview_time
        FROM interviews
        WHERE student_id=%s
        """,
        (student_id,)
    )

    interviews = cursor.fetchall()

    return render_template(
        'my_interviews.html',
        interviews=interviews
    )

@app.route('/admin-logout')
def admin_logout():

    session.pop('admin', None)

    return redirect('/admin-login')

@app.route('/selected-students')
def selected_students():

    sql = """
    SELECT applications.student_id,
           jobs.company_name
    FROM applications
    JOIN jobs
    ON applications.job_id = jobs.id
    WHERE applications.status='Selected'
    """

    cursor.execute(sql)

    students = cursor.fetchall()

    return render_template(
        'selected_students.html',
        students=students
    )

@app.route('/company-results')
def company_results():

    sql = """
    SELECT jobs.company_name,
           COUNT(*) as selected_count
    FROM applications
    JOIN jobs
    ON applications.job_id = jobs.id
    WHERE applications.status='Selected'
    GROUP BY jobs.company_name
    """

    cursor.execute(sql)

    results = cursor.fetchall()

    return render_template(
        'company_results.html',
        results=results
    )

@app.route('/placement-status')
def placement_status():

    student_id = session.get('student_id')

    cursor.execute(
        """
        SELECT status
        FROM applications
        WHERE student_id=%s
        """,
        (student_id,)
    )

    statuses = cursor.fetchall()

    return render_template(
        'placement_status.html',
        statuses=statuses
    )


@app.route('/notifications')
def notifications():

    student_id = session['student_id']

    cursor.execute(
        """
        SELECT message, created_at
        FROM notifications
        WHERE student_id=%s
        ORDER BY created_at DESC
        """,
        (student_id,)
    )

    notifications = cursor.fetchall()

    return render_template(
        'notifications.html',
        notifications=notifications
    )

@app.route('/send-notification', methods=['GET', 'POST'])
def send_notification():

    if request.method == 'POST':

        student_id = request.form['student_id']
        notification_type = request.form['notification_type']
        message = request.form['message']

        # Get student email
        cursor.execute(
            "SELECT email FROM students WHERE id=%s",
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            flash(
    "❌ Student Not Found",
    "danger"
)

            return redirect(url_for('send_notification'))

        student_email = student[0]

        print("Sending Email To:", student_email)

        try:

            msg = Message(
                notification_type,
                sender='jaykoladiya2409@gmail.com',
                recipients=[student_email]
            )

            msg.body = message

            mail.send(msg)

            flash(
    "✅ Notification Sent Successfully",
    "success"
)

            return redirect(url_for('send_notification'))

        except Exception as e:

            flash(
    f"❌ Email Error: {e}",
    "danger"
)

        return redirect(url_for('send_notification'))

    return render_template('send_notification.html')
if __name__ == '__main__':
    app.run(debug=True)