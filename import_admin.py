import mysql.connector
from werkzeug.security import generate_password_hash

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="smart_canteen"
)

cursor = db.cursor()

# Admin credentials
admin_id = "admin"
admin_password = "canteen@123"

# Hash the password
hashed_password = generate_password_hash(admin_password)

try:
    cursor.execute(
        """
        INSERT INTO users
        (college_id, password_hash, user_type)
        VALUES (%s, %s, %s)
        """,
        (admin_id, hashed_password, "admin")
    )

    db.commit()
    print("Admin added successfully!")

except mysql.connector.IntegrityError:
    print("Admin account already exists!")

cursor.close()
db.close()