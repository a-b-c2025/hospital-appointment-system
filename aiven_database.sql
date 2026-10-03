-- Cloud Hospital Appointment System: schema for the cloud database (Aiven MySQL).
-- Same as final_database_file.sql, with lowercase table names to match app.py.
-- No CREATE DATABASE: Aiven gives you "defaultdb" already.

CREATE TABLE IF NOT EXISTS patient_details (
    Patient_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INT,
    Gender VARCHAR(10),
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(15),
    Address VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS doctor (
    Doctor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Specialization VARCHAR(100),
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS appointment (
    Appointment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    Doctor_ID INT,
    Appointment_Date DATE,
    Appointment_Time TIME,
    Reason VARCHAR(200),
    Status VARCHAR(30) DEFAULT 'Pending',
    FOREIGN KEY (Patient_ID) REFERENCES patient_details(Patient_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES doctor(Doctor_ID)
);

CREATE TABLE IF NOT EXISTS hospital_admin (
    Admin_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(15),
    Username VARCHAR(50) UNIQUE,
    Password VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS doctor_availability (
    Availability_ID INT AUTO_INCREMENT PRIMARY KEY,
    Doctor_ID INT,
    Available_Day VARCHAR(20),
    Start_Time TIME,
    End_Time TIME,
    FOREIGN KEY (Doctor_ID) REFERENCES doctor(Doctor_ID)
);

-- Doctors (same names as doctors.html / appointment.html). INSERT IGNORE skips them if already added.
INSERT IGNORE INTO doctor (Doctor_ID, Name, Specialization) VALUES
    (1, 'Dr. Rahul Sharma', 'Cardiologist'),
    (2, 'Dr. Priya Patil', 'General Physician'),
    (3, 'Dr. Amit Joshi', 'Dermatologist'),
    (4, 'Dr. Sneha Kulkarni', 'Pediatrician'),
    (5, 'Dr. Rohan Mehta', 'Orthopedic'),
    (6, 'Dr. Karan Shah', 'Neurologist'),
    (7, 'Dr. Vikram Joshi', 'Dentist');
