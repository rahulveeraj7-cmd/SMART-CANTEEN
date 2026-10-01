import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_LOCAL_MYSQL_PASSWORD",
    database="smart_canteen"
)

cursor = conn.cursor()

new_password = "Faculty@123"
password_hash = generate_password_hash(new_password)

cursor.execute(
    """
    UPDATE users
    SET password_hash = ?
    WHERE college_id = ?
    """.replace("?", "%s"),
    (password_hash, "FAC001")
)

conn.commit()

print("Faculty password updated successfully.")

cursor.close()
conn.close()
