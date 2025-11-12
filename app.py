from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime,timezone
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import pandas as pd
import io
import os
import smtplib
from functools import wraps
import sqlite3
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import re
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'admin':
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('menu'))
        return f(*args, **kwargs)
    return decorated_function
app = Flask(__name__)
app.secret_key = '59c32376f655614c8f67ca5ac4d218d4578af6be525fc8b3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Mail configuration (update with your credentials)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'aradhyamanokaran@gmail.com'
app.config['MAIL_PASSWORD'] = 'xksb vcxq hxuy yuyu'
mail = Mail(app)
db = SQLAlchemy(app)
# -------------------- Models --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_role = db.Column(db.String(50))
    staffid = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))
    name = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    designation = db.Column(db.String(100))
    institution = db.Column(db.String(100))
class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(50))
    login_time = db.Column(db.DateTime)
    logout_time = db.Column(db.DateTime)
class FDPAttended(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffid = db.Column(db.String(50))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    programme_attended = db.Column(db.String(100))
    from_date = db.Column(db.String(20))
    to_date = db.Column(db.String(20))
    organizer = db.Column(db.String(100))
    sponsor = db.Column(db.String(100))
    no_of_days = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
class FDPConducted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffid = db.Column(db.String(50))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    programme_attended = db.Column(db.String(100))
    from_date = db.Column(db.String(20))
    to_date = db.Column(db.String(20))
    organizer = db.Column(db.String(100))
    sponsor = db.Column(db.String(100))
    no_of_days = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
class ConferenceAttended(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffid = db.Column(db.String, nullable=False)
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    programme_attended = db.Column(db.String(100))
    from_date = db.Column(db.String(20))
    to_date = db.Column(db.String(20))
    organizer = db.Column(db.String(100))
    sponsor = db.Column(db.String(100))
    no_of_days = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
class ConferenceConducted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffid = db.Column(db.String(50))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    programme_attended = db.Column(db.String(100))
    from_date = db.Column(db.String(20))
    to_date = db.Column(db.String(20))
    organizer = db.Column(db.String(100))
    sponsor = db.Column(db.String(100))
    no_of_days = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
class LectureConducted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffid = db.Column(db.String(50))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    programme_attended = db.Column(db.String(100))
    from_date = db.Column(db.String(20))
    to_date = db.Column(db.String(20))
    organizer = db.Column(db.String(100))
    sponsor = db.Column(db.String(100))
    no_of_days = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
class ExtractedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffid = db.Column(db.String(50))
    name = db.Column(db.String(100))
    certificate_type = db.Column(db.String(100))
    date = db.Column(db.String(20))
def extract_certificate_fields(text):
    fields = {
        'name': "Not Available",
        'designation': "Not Available",
        'department': "Not Available",
        'programme_attended': "Not Available",
        'from_date': None,
        'to_date': None,
        'organizer': "Not Available",
        'sponsor': "Not Available",
        'no_of_days': "Not Available"
    }
    # Extract Name
    name_match = re.search(r'This is to certify that\s+(.*?),', text, re.IGNORECASE)
    if name_match:
        fields['name'] = name_match.group(1).strip()
    # Extract Designation
    desig_match = re.search(r',\s*([A-Za-z ]*Professor)[,\n]', text)
    if desig_match:
        fields['designation'] = desig_match.group(1).strip()
    # Extract Department
    dept_match = re.search(r'Department of ([A-Za-z &]+)', text, re.IGNORECASE)
    if dept_match:
        fields['department'] = dept_match.group(1).strip()
    # Extract Programme Attended robustly
    prog_match = re.search(r'on\s*[“"]([^”"]+)[”"]', text, re.IGNORECASE)  # handles “ ” and " "
    if prog_match:
        fields['programme_attended'] = prog_match.group(1).strip()
    else:
        # Try without quotes
        prog_match_alt = re.search(r'(Programme|program)\s+on\s+([A-Za-z0-9 ,\-&]+)', text, re.IGNORECASE)
        if prog_match_alt:
            fields['programme_attended'] = prog_match_alt.group(2).strip()
        else:
            fields['programme_attended'] = "Not Available"
    # Extract From and To Dates
    date_match = re.search(r'from (\d{2}-\d{2}-\d{4}) to (\d{2}-\d{2}-\d{4})', text)
    if date_match:
        fields['from_date'] = datetime.strptime(date_match.group(1), '%d-%m-%Y').date()
        fields['to_date'] = datetime.strptime(date_match.group(2), '%d-%m-%Y').date()
        fields['no_of_days'] = (fields['to_date'] - fields['from_date']).days + 1
    # Organizer
    organizer_match = re.search(r'organized by\s+(.*?)(?:,|\n)', text, re.IGNORECASE)
    if organizer_match:
        fields['organizer'] = organizer_match.group(1).strip()
    # Sponsor
    sponsor_match = re.search(r'association with\s+(.*?)(?:,|\n)', text, re.IGNORECASE)
    if sponsor_match:
        fields['sponsor'] = sponsor_match.group(1).strip()
    return fields
# -------------------- Routes --------------------
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/menu')
def menu():
    if 'staffid' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))
    staffid = session.get('staffid')
    name = session.get('name')
    login_time = session.get('login_time')
    return render_template('menu.html', staffid=staffid, name=name, login_time=login_time)
# Example login route to expand
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        staffid = request.form['staffid']
        password = request.form['password']
        user = User.query.filter_by(staffid=staffid).first()
        if user:
            if user and user.password == password:
                session['staffid'] = user.staffid
                session['name'] = user.name
                session['user_role'] = user.user_role
                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                session['login_time'] = login_time
                # Optionally log in the LoginHistory table:
                login_history = LoginHistory(staff_id=user.staffid, login_time=datetime.now())
                db.session.add(login_history)
                db.session.commit()
                flash("Login successful!", "success")
                return redirect(url_for('menu'))
            else:
                flash('Incorrect password.', 'error')
        else:
            flash('Staff ID not registered, please register first.', 'error')
            return redirect(url_for('register'))
    return render_template('login.html')
# -------------------- Initialization --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_role = request.form['user_role']
        staffid = request.form['staffid']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        contact_number = request.form['contact_number']
        designation = request.form['designation']
        institution = request.form['institution']
        # Enforce single admin policy
        if staffid == 'staff001' and password == 'password123':
            user_role = 'admin'
        else:
            user_role = 'user'
        existing_user = User.query.filter_by(staffid=staffid).first()
        if existing_user:
            flash('Staff ID already exists. Please login.', 'danger')
            return redirect(url_for('login'))
        new_user = User(user_role=user_role, staffid=staffid, password=password,
                        email=email, name=name, contact_number=contact_number,
                        designation=designation, institution=institution)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
# -------------------- Forgot Password --------------------
@app.route('/text_extraction', methods=['GET', 'POST'])
def text_extraction():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.lower().endswith(('.jpg', '.jpeg')):
            image = Image.open(file)
            extracted_text = pytesseract.image_to_string(image)
            return render_template('extracted_text.html', extracted_text=extracted_text)
        else:
            flash('Please upload a JPG or JPEG file.', 'danger')
            return redirect(url_for('text_extraction'))
    return render_template('text_extraction.html')
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        staffid = request.form['staffid']
        user = User.query.filter_by(staffid=staffid).first()
        if user:
            msg = Message('Password Reset',
              sender=app.config['MAIL_USERNAME'],  # ✅
              recipients=[user.email])
            msg.body = f"Your password is: {user.password}"
            mail.send(msg)
            flash('Password sent to your registered email.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Staff ID not found.', 'error')
    return render_template('forgot_password.html')
# -------------------- Logout --------------------
@app.route('/test_mail')
def test_mail():
    msg = Message('Test Email from FDP System',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=['aradhyamanokaran@gmail.com'])  # test with your own mail
    msg.body = "This is a test email to verify Flask-Mail configuration."
    try:
        mail.send(msg)
        return "Test mail sent successfully."
    except Exception as e:
        return f"Error: {e}"
@app.route('/logout')
def logout():
    staffid = session.get('staffid')
    if staffid:
        login_record = LoginHistory.query.filter_by(staff_id=staffid).order_by(LoginHistory.id.desc()).first()
        if login_record and login_record.logout_time is None:
            login_record.logout_time = datetime.now()
            db.session.commit()
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))
# -------------------- Upload with OCR --------------------
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'staffid' not in session:
        return redirect(url_for('login'))
    extracted_text = None
    if request.method == 'POST':
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # OCR extraction
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image)
            extracted_text = text
            # Field extraction
            fields = extract_certificate_fields(text)
            fields['department'] = fields.get('department') or 'Not Available'
            fields['organizer'] = fields.get('organizer') or 'Not Available'
            fields['sponsor'] = fields.get('sponsor') or 'Not Available'
            fields['programme_attended'] = fields.get('programme_attended') or 'Not Available'
            # Auto category detection
            category = None
            if 'FACULTY DEVELOPMENT' in text.upper() or 'FDP' in text.upper():
                category = 'fdp_attended'
            elif 'CONFERENCE CONDUCTED' in text.upper():
                category = 'conference_conducted'
            elif 'FACULTY DEVELOPMENT PROGRAMME CONDUCTED' in text.upper():
                category = 'fdp_conducted'
            elif 'CONFERENCE' in text.upper():
                category = 'conference_attended'
            elif 'LECTURE' in text.upper():
                category = 'lecture_conducted'
            # Insert into appropriate table
            record = None
            staffid = session.get('staffid')

            if category == 'fdp_attended':
                record = FDPAttended(
                    staffid=staffid,
                    name=fields['name'],
                    designation=fields['designation'],
                    department=fields['department'],
                    programme_attended=fields['programme_attended'],
                    from_date=fields['from_date'],
                    to_date=fields['to_date'],
                    organizer=fields['organizer'],
                    sponsor=fields['sponsor'],
                    no_of_days=fields['no_of_days'],
                    filename=filename,  # ✅ Ensure this
                    created_on = datetime.now(timezone.utc)
                )
            elif category == 'conference_attended':
                record = ConferenceAttended(
                    staffid=staffid,
                    name=fields['name'],
                    designation=fields['designation'],
                    department=fields['department'],
                    conference_name=fields['programme_attended'],
                    from_date=fields['from_date'],
                    to_date=fields['to_date'],
                    organizer=fields['organizer'],
                    sponsor=fields['sponsor'],
                    no_of_days=fields['no_of_days'],
                    filename=filename,  # ✅ Ensure this
                    created_on = datetime.now(timezone.utc)
                )
            elif category == 'lecture_conducted':
                record = LectureConducted(
                    staffid=staffid,
                    name=fields['name'],
                    designation=fields['designation'],
                    department=fields['department'],
                    topic=fields['programme_attended'],
                    date=fields['from_date'],
                    organizer=fields['organizer'],
                    sponsor=fields['sponsor'],
                    no_of_days=fields['no_of_days'],
                    filename=filename,  # ✅ Ensure this
                    created_on = datetime.now(timezone.utc)
                )
            elif category == 'fdp_conducted':
                record = FDPConducted(
                    staffid=staffid,
                    name=fields['name'],
                    designation=fields['designation'],
                    department=fields['department'],
                    fdp_title=fields['programme_attended'],
                    from_date=fields['from_date'],
                    to_date=fields['to_date'],
                    organizer=fields['organizer'],
                    sponsor=fields['sponsor'],
                    no_of_days=fields['no_of_days'],
                    filename=filename,  # ✅ Ensure this
                    created_on = datetime.now(timezone.utc)
                )
            elif category == 'conference_conducted':
                record = ConferenceConducted(
                    staffid=staffid,
                    name=fields['name'],
                    designation=fields['designation'],
                    department=fields['department'],
                    conference_title=fields['programme_attended'],
                    from_date=fields['from_date'],
                    to_date=fields['to_date'],
                    organizer=fields['organizer'],
                    sponsor=fields['sponsor'],
                    no_of_days=fields['no_of_days'],
                    filename=filename,  # ✅ Ensure this
                    created_on = datetime.now(timezone.utc)
                )

            if record:
                db.session.add(record)
                db.session.commit()

            return render_template('upload.html', extracted_text=text, success=True)

    return render_template('upload.html', extracted_text=extracted_text)

@app.route('/view_uploads')
def view_uploads():
    if 'staffid' not in session:
        return redirect(url_for('login'))

    staffid = session['staffid']

    uploads = []

    uploads.extend(FDPAttended.query.filter_by(staffid=staffid).all())
    uploads.extend(ConferenceAttended.query.filter_by(staffid=staffid).all())
    uploads.extend(FDPConducted.query.filter_by(staffid=staffid).all())
    uploads.extend(ConferenceConducted.query.filter_by(staffid=staffid).all())
    uploads.extend(LectureConducted.query.filter_by(staffid=staffid).all())

    # Sort by upload date descending
    uploads.sort(key=lambda x: x.created_on or datetime.min, reverse=True)

    return render_template('view_uploads.html', uploads=uploads)





@app.route('/view_all_uploads', methods=['GET', 'POST'])
def view_all_uploads():
    uploads = []
    staffid = None

    if request.method == 'POST':
        staffid = request.form.get('staffid')
        if staffid:
            uploads.extend(FDPAttended.query.filter_by(staffid=staffid).all())
            uploads.extend(ConferenceAttended.query.filter_by(staffid=staffid).all())
            uploads.extend(FDPConducted.query.filter_by(staffid=staffid).all())
            uploads.extend(ConferenceConducted.query.filter_by(staffid=staffid).all())
            uploads.extend(LectureConducted.query.filter_by(staffid=staffid).all())

            uploads.sort(key=lambda x: x.created_on or datetime.min, reverse=True)

    return render_template('view_all_uploads.html', uploads=uploads, staffid=staffid)




# -------------------- Search with CSV Export --------------------
@app.route('/uploads')
def uploads():
    if 'staffid' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))

    staffid = session.get('staffid')
    uploads = FDPAttended.query.filter_by(staffid=staffid).all()

    return render_template('uploads.html', uploads=uploads)



@app.route('/history')
@admin_only
def history():
    if 'staffid' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))

    # Allow only admin
    user_role = session.get('user_role')
    if user_role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('menu'))

    histories = LoginHistory.query.all()
    return render_template('history.html', histories=histories)

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        category = request.form['category']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        name = request.form['name']

        table_map = {
            'fdp_attended': FDPAttended,
            'fdp_conducted': FDPConducted,
            'conference_attended': ConferenceAttended,
            'conference_conducted': ConferenceConducted,
            'lecture_conducted': LectureConducted
        }

        Model = table_map.get(category)
        if Model:
            query = Model.query
            if name:
                query = query.filter(Model.name.ilike(f"%{name}%"))
            if start_date:
                query = query.filter(Model.from_date >= start_date)
            if end_date:
                query = query.filter(Model.to_date <= end_date)

            results = query.all()

            if request.form.get('action') == 'export':
                data = [{
                    'Name': r.name,
                    'Designation': r.designation,
                    'Department': r.department,
                    'Programme': r.programme_attended,
                    'From': r.from_date,
                    'To': r.to_date,
                    'Organizer': r.organizer,
                    'Sponsor': r.sponsor,
                    'Days': r.no_of_days
                } for r in results]
                df = pd.DataFrame(data)
                output = io.BytesIO()
                df.to_csv(output, index=False)
                output.seek(0)
                return send_file(output, download_name='search_results.csv', as_attachment=True)

    return render_template('search.html', results=results)



# -------------------- View & Edit Profile --------------------

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'staffid' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(staffid=session['staffid']).first()
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.contact_number = request.form['contact_number']
        user.designation = request.form['designation']
        user.institution = request.form['institution']
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

# -------------------- Admin: View Uploads & History --------------------

@app.route('/admin_uploads', methods=['GET', 'POST'])
@admin_only
def admin_uploads():
    uploads = []
    if request.method == 'POST':
        staffid = request.form['staffid']
        uploads = ExtractedData.query.filter_by(name=staffid).all()
    return render_template('admin_uploads.html', uploads=uploads)

@app.route('/admin_history')
@admin_only
def admin_history():
    history = LoginHistory.query.order_by(LoginHistory.id.desc()).all()
    return render_template('admin_history.html', history=history)

# -------------------- Initialization --------------------

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("All tables deleted and recreated successfully.")
    app.run(debug=True)


