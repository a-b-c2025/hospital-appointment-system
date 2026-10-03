import os
import mysql.connector


def get_db_connection():
    # Locally these defaults are used; on the hosting site set the
    # DB_HOST / DB_USER / DB_PASSWORD / DB_NAME / DB_PORT environment variables.
    connection = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "admin123"),
        database=os.environ.get("DB_NAME", "Cloud_Hospital_Appointment")
    )

    return connection
