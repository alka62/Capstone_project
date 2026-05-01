import streamlit as st
import sqlite3
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np

# =========================

# DATABASE CONNECTION

# =========================

conn = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = conn.cursor()

# =========================

# CREATE TABLES

# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_name TEXT,
    department TEXT,
    available_slots INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    doctor_name TEXT,
    department TEXT,
    priority TEXT,
    wait_time INTEGER,
    status TEXT
)
""")
conn.commit()

# =========================

# DEFAULT ADMIN

# =========================

cursor.execute("SELECT * FROM users WHERE username='admin'")
admin = cursor.fetchone()
if not admin:
    cursor.execute("""
    INSERT INTO users (username, password, role)
    VALUES (?, ?, ?)
    """, ("admin", "admin123", "admin"))
    conn.commit()

# ============dxm=============

# INSERT DOCTORS IF EMPTY

# =========================

cursor.execute("SELECT COUNT(*) FROM doctors")
count = cursor.fetchone()[0]

if count == 0:
    doctors_data = [
        ("Dr. Sharma", "Cardiology", 5),
        ("Dr. Verma", "Cardiology", 4),
        ("Dr. Mehta", "Neurology", 4),
        ("Dr. Rao", "Neurology", 3),
        ("Dr. Singh", "Orthopedic", 3),
        ("Dr. Patel", "Orthopedic", 4),
        ("Dr. Khan", "General", 6),
        ("Dr. Gupta", "General", 5),
        ("Dr. Roy", "Dermatology", 4),
        ("Dr. Das", "Dermatology", 3),
        ("Dr. Nair", "Pediatrics", 5),
        ("Dr. Iyer", "Pediatrics", 4),
        ("Dr. Kapoor", "ENT", 3),
        ("Dr. Bansal", "ENT", 4),
        ("Dr. Arora", "Surgery", 2),
        ("Dr. Thomas", "Surgery", 3)
    ]

    cursor.executemany("""
    INSERT INTO doctors (doctor_name, department, available_slots)
    VALUES (?, ?, ?)
    """, doctors_data)
    conn.commit()

# =========================

# SESSION STATE

# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# =========================

# LOGIN PAGE

# =========================

def login():
    st.title("Hospital Appointments, Queue and Wait Time Prediction System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    role = st.selectbox("Login As", ["patient", "admin"])

    if st.button("Login"):
        cursor.execute("""
            SELECT * FROM users
            WHERE username=? AND password=? AND role=?
        """, (username, password, role))

        user = cursor.fetchone()

        if user:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.username = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.subheader("New Patient Registration")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (new_user, new_pass, "patient"))
            conn.commit()
            st.success("Patient registered successfully")
        except:
            st.error("Username already exists")

# =========================

# PATIENT DASHBOARD

# =========================

def patient_dashboard():
    st.title(f"Welcome, {st.session_state.username.capitalize()}")
    st.subheader("Patient Dashboard")


    doctors_df = pd.read_sql("SELECT * FROM doctors", conn)

    department = st.selectbox(
        "Select Department",
        doctors_df["department"].unique()
    )

    filtered_doctors = doctors_df[
        doctors_df["department"] == department
    ]

    doctor_name = st.selectbox(
        "Select Doctor",
        filtered_doctors["doctor_name"]
    )

    priority = st.selectbox(
        "Priority",
        ["Normal", "Emergency"]
    )

    if st.button("Book Appointment"):
        queue_count = pd.read_sql("""
            SELECT COUNT(*) as total
            FROM appointments
            WHERE doctor_name=?
        """, conn, params=(doctor_name,))["total"][0]

        if priority == "Emergency":
            wait_time = 0
            status = "Emergency Priority"
        else:
            wait_time = int(queue_count) * 10
            status = "Booked"

        cursor.execute("""
            INSERT INTO appointments
            (patient_name, doctor_name, department, priority, wait_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            st.session_state.username,
            doctor_name,
            department,
            priority,
            wait_time,
            status
        ))
        conn.commit()

        st.success("Appointment Booked")
        st.info(f"Estimated Wait Time: {wait_time} minutes")

    st.subheader("My Appointments")

    my_appointments = pd.read_sql("""
        SELECT * FROM appointments
        WHERE patient_name=?
    """, conn, params=(st.session_state.username,))

    my_appointments["wait_time"] = my_appointments["wait_time"].astype(str) + " minutes"
    st.dataframe(my_appointments)

# =========================

# ADMIN DASHBOARD

# =========================

def admin_dashboard():
    st.title("Admin Dashboard")

    # Add Doctor Section
    st.subheader("Add Doctor")

    doctor_name = st.text_input("Doctor Name")
    department = st.text_input("Department")

    if st.button("Add Doctor"):
        cursor.execute(
            "INSERT INTO doctors (doctor_name, department) VALUES (?, ?)",
            (doctor_name, department)
        )
        conn.commit()
        st.success("Doctor added successfully")

    # All Appointments
    st.subheader("All Appointments")

    appointments = pd.read_sql("""
        SELECT appointment_id, patient_name, doctor_name, department, priority, wait_time, status
        FROM appointments
    """, conn)

    appointments["wait_time"] = appointments["wait_time"].astype(str) + " minutes"
    st.dataframe(appointments)

    # Emergency Patients
    st.subheader("Emergency Patients")

    emergency = pd.read_sql("""
        SELECT appointment_id, patient_name, doctor_name, department, priority, wait_time, status
        FROM appointments
        WHERE priority='Emergency'
    """, conn)

    emergency["wait_time"] = emergency["wait_time"].astype(str) + " minutes"
    st.dataframe(emergency)

    # Approve Appointment
    st.subheader("Approve Appointment")

    approve_id = st.number_input("Appointment ID to Approve", min_value=1, step=1)

    if st.button("Approve Appointment"):
        cursor.execute("""
            UPDATE appointments
            SET status='Approved'
            WHERE appointment_id=?
        """, (approve_id,))
        conn.commit()
        st.success("Appointment approved")

    # Cancel Appointment
    st.subheader("Cancel Appointment")

    cancel_id = st.number_input("Appointment ID to Cancel", min_value=1, step=1)

    if st.button("Cancel Appointment"):
        cursor.execute("""
            UPDATE appointments
            SET status='Cancelled'
            WHERE appointment_id=?
        """, (cancel_id,))
        conn.commit()
        st.warning("Appointment cancelled")

    # Average Wait Time
    st.subheader("Average Wait Time")

    avg_wait = pd.read_sql("""
        SELECT AVG(wait_time) as avg_wait
        FROM appointments
        WHERE status='Approved'
    """, conn)

    st.write("Average Wait Time:", round(avg_wait["avg_wait"][0], 2), "minutes")

def wait_time_prediction():
    st.title("Wait Time Prediction")

    appointments_df = pd.read_sql("SELECT * FROM appointments", conn)

    appointments_df["wait_time"] = pd.to_numeric(appointments_df["wait_time"], errors="coerce")
    appointments_df = appointments_df.dropna()

    if len(appointments_df) > 1:

        # Encoding categorical columns
        le_priority = LabelEncoder()
        le_department = LabelEncoder()

        appointments_df["priority_encoded"] = le_priority.fit_transform(appointments_df["priority"])
        appointments_df["department_encoded"] = le_department.fit_transform(appointments_df["department"])
        appointments_df["queue_position"] = range(1, len(appointments_df)+1)

        # Features and target
        X = appointments_df[["priority_encoded", "department_encoded", "queue_position"]]
        y = appointments_df["wait_time"]

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Accuracy
        predictions = model.predict(X)
        accuracy = r2_score(y, predictions)

        st.subheader("Model Performance")
        st.write("Model Accuracy (R² Score):", round(accuracy, 2))

        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))

        st.write("MAE:", round(mae, 2))
        st.write("RMSE:", round(rmse, 2))
        # User inputs for prediction
        st.subheader("Predict Wait Time for New Patient")

        priority_input = st.selectbox("Select Priority", ["Normal", "Emergency"])
        department_input = st.selectbox("Select Department", appointments_df["department"].unique())
        queue_input = st.number_input("Queue Position", min_value=1, step=1)

        priority_encoded = le_priority.transform([priority_input])[0]
        department_encoded = le_department.transform([department_input])[0]

        predicted_wait = model.predict([[priority_encoded, department_encoded, queue_input]])[0]

        st.success(f"Predicted Wait Time: {round(predicted_wait,2)} minutes")

    else:
        st.warning("Not enough data for prediction")

def wait_time_analysis():
    st.title("Wait Time Analysis")

    appointments_df = pd.read_sql("SELECT * FROM appointments", conn)
    appointments_df["wait_time"] = pd.to_numeric(appointments_df["wait_time"], errors="coerce")
    appointments_df = appointments_df.dropna()

    if len(appointments_df) > 0:
        st.line_chart(appointments_df["wait_time"])

        dept_analysis = pd.read_sql("""
            SELECT department, AVG(wait_time) as avg_wait
            FROM appointments
            GROUP BY department
        """, conn)

        st.subheader("Department Wise Average Wait Time")
        st.bar_chart(dept_analysis.set_index("department"))

    else:
        st.warning("No data available")

def priority_analysis():
    st.title("Priority Analysis")

    analysis_df = pd.read_sql("""
        SELECT priority, AVG(wait_time) as avg_wait
        FROM appointments
        GROUP BY priority
    """, conn)

    display_df = analysis_df.copy()
    display_df["avg_wait"] = display_df["avg_wait"].astype(str) + " minutes"

    st.dataframe(display_df)
    st.bar_chart(analysis_df.set_index("priority"))

# =========================

# MAIN APP

# =========================

if not st.session_state.logged_in:
    login()
elif st.session_state.logged_in and st.session_state.role == "admin":
    st.sidebar.write("Logged in as:", st.session_state.username)
    st.sidebar.write("Role:", st.session_state.role)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    page = st.sidebar.radio(
        "Select Page",
        [
            "Admin Dashboard",
            "Wait Time Prediction",
            "Wait Time Analysis",
            "Priority Analysis"
        ]
    )

    if page == "Admin Dashboard":
        admin_dashboard()
    elif page == "Wait Time Prediction":
        wait_time_prediction()
    elif page == "Wait Time Analysis":
        wait_time_analysis()
    elif page == "Priority Analysis":
        priority_analysis()

elif st.session_state.logged_in and st.session_state.role == "patient":
    st.sidebar.write("Logged in as:", st.session_state.username)
    st.sidebar.write("Role:", st.session_state.role)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    patient_dashboard()
