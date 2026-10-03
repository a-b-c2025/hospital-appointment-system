import os
from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory, abort
from database import get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

app = Flask(__name__, static_folder=os.path.join(PROJECT_DIR, "static"), static_url_path="/static")

app.secret_key = os.environ.get("SECRET_KEY", "hospital123")


def message_page(title, text, buttons, error=False):
    """Styled success / error page (templates/message.html)."""
    return render_template("message.html", title=title, text=text,
                           buttons=buttons, error=error)


# ---------------- HTML PAGES (index.html, login.html, appointment.html ...) ----------------

@app.route("/<page>.html")
def html_page(page):
    path = os.path.join(PROJECT_DIR, page + ".html")
    if not os.path.isfile(path):
        abort(404)
    return send_from_directory(PROJECT_DIR, page + ".html")


# ---------------- HOME ----------------

@app.route("/")
def home():
    if os.path.isfile(os.path.join(PROJECT_DIR, "index.html")):
        return send_from_directory(PROJECT_DIR, "index.html")
    return redirect("/login.html")


@app.route("/health")
def health():
    connection = get_db_connection()

    if connection.is_connected():
        connection.close()
        return "Flask connected to MySQL successfully"

    return "Database connection failed"


# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO patient_details
        (Name, Age, Gender, Email, Phone, Address)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        age,
        gender,
        email,
        phone,
        address
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return message_page("Registration successful", "Your account is ready. Log in with your email and mobile number.", [("Log in", "/login.html"), ("Back to home", "/index.html")])


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    phone = request.form["phone"]

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT Patient_ID, Name
        FROM patient_details
        WHERE Email = %s AND Phone = %s
    """

    cursor.execute(query, (email, phone))

    patient = cursor.fetchone()

    cursor.close()
    connection.close()

    if patient is None:
        return message_page("Login failed", "No patient matches that email and mobile number. Check both and try again, or register if you are new.", [("Try again", "/login.html"), ("Register", "/register.html")], error=True)

    session["patient_id"] = patient[0]
    session["patient_name"] = patient[1]

    return message_page("Welcome, " + str(patient[1]), "You are logged in. Book a new appointment or check the status of your existing ones.", [("Book an appointment", "/appointment.html"), ("My appointments", "/my_appointments")])


# ---------------- BOOK APPOINTMENT ----------------

@app.route("/book_appointment", methods=["POST"])
def book_appointment():

    patient_name = request.form["patient_name"]
    doctor_name = request.form["doctor_name"]
    appointment_date = request.form["appointment_date"]
    appointment_time = request.form["appointment_time"]
    reason = request.form["reason"]

    connection = get_db_connection()
    cursor = connection.cursor()

    # Use logged-in patient if available
    patient_id = session.get("patient_id")

    if patient_id is None:

        # Find patient from database
        patient_query = """
            SELECT Patient_ID
            FROM patient_details
            WHERE LOWER(TRIM(Name)) = LOWER(TRIM(%s))
        """

        cursor.execute(patient_query, (patient_name,))
        patient = cursor.fetchone()

        if patient is None:

            cursor.close()
            connection.close()

            return message_page("Patient not found", "No registered patient has that name. Use the exact name you registered with, or register first.", [("Register", "/register.html"), ("Try again", "/appointment.html")], error=True)

        patient_id = patient[0]

        # Store patient in session
        session["patient_id"] = patient_id
        session["patient_name"] = patient_name

    # Find doctor from database
    doctor_query = """
        SELECT Doctor_ID
        FROM doctor
        WHERE LOWER(TRIM(Name)) = LOWER(TRIM(%s))
    """

    cursor.execute(doctor_query, (doctor_name,))
    doctor = cursor.fetchone()

    if doctor is None:

        cursor.close()
        connection.close()

        return message_page("Doctor not found", "Choose a doctor from the list and try again.", [("Try again", "/appointment.html")], error=True)

    doctor_id = doctor[0]

    # Store appointment in database
    appointment_query = """
        INSERT INTO appointment
        (
            Patient_ID,
            Doctor_ID,
            Appointment_Date,
            Appointment_Time,
            Reason,
            Status
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        reason,
        "Pending"
    )

    cursor.execute(appointment_query, values)

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("my_appointments"))


# ---------------- MY APPOINTMENTS ----------------

@app.route("/my_appointments")
def my_appointments():

    patient_id = session.get("patient_id")

    if patient_id is None:
        return message_page("Please log in first", "Log in with your email and mobile number to see your appointments.", [("Log in", "/login.html"), ("Register", "/register.html")], error=True)

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            doctor.Name,
            appointment.Appointment_Date,
            appointment.Appointment_Time,
            appointment.Status
        FROM appointment
        JOIN doctor
        ON appointment.Doctor_ID = doctor.Doctor_ID
        WHERE appointment.Patient_ID = %s
    """

    cursor.execute(query, (patient_id,))

    appointments = cursor.fetchall()

    patient_name = session.get("patient_name")

    cursor.close()
    connection.close()

    return render_template(
        "my_appointments.html",
        appointments=appointments,
        patient_name=patient_name
    )


# ---------------- DOCTOR DASHBOARD ----------------

@app.route("/doctor_dashboard")
def doctor_dashboard():

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            appointment.Appointment_ID,
            patient_details.Name,
            doctor.Name,
            appointment.Appointment_Date,
            appointment.Appointment_Time,
            appointment.Status
        FROM appointment
        JOIN patient_details
        ON appointment.Patient_ID = patient_details.Patient_ID
        JOIN doctor
        ON appointment.Doctor_ID = doctor.Doctor_ID
        ORDER BY appointment.Appointment_ID
    """

    cursor.execute(query)

    # Gets only appointments stored in MySQL
    appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        appointments=appointments
    )


# ---------------- CONFIRM / REJECT ----------------

@app.route("/update_appointment/<int:appointment_id>/<status>")
def update_appointment(appointment_id, status):

    if status not in ["Confirmed", "Rejected"]:
        return message_page("Invalid status", "An appointment can only be Confirmed or Rejected.", [("Back to dashboard", "/doctor_dashboard")], error=True)

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE appointment
        SET Status = %s
        WHERE Appointment_ID = %s
    """

    cursor.execute(
        query,
        (status, appointment_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("doctor_dashboard"))


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return message_page("You are logged out", "You have been logged out safely.", [("Back to home", "/index.html"), ("Log in again", "/login.html")])


# ---------------- ADMIN LOGIN PAGE ----------------

@app.route("/admin_login_page")
def admin_login_page():
    return redirect("/admin_login.html")


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["POST"])
def admin_login():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":

        session["admin"] = True

        return redirect(url_for("doctor_dashboard"))

    return message_page("Admin login failed", "The username or password is incorrect. Check both and try again.", [("Try again", "/admin_login.html")], error=True)


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))