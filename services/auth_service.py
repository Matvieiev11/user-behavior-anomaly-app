import hashlib
from datetime import datetime

from utils.database import get_connection

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def generate_username(email: str) -> str:
    return email.split("@")[0].strip()

def find_user_by_email(email: str):
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, email, username, password_hash
            FROM users
            WHERE lower(email) = lower(?)
        """, (email,))

        row = cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "email": row[1],
                "username": row[2],
                "password_hash": row[3]
            }

        return None

def register_user(email: str, password: str):
    email = email.strip()

    if not email or "@" not in email:
        return False, "Invalid email address."

    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long."

    if find_user_by_email(email):
        return False, "User with this email already exists."

    username = generate_username(email)
    password_hash = hash_password(password)

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (
                email,
                username,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            email,
            username,
            password_hash,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()

    return True, {
        "email": email,
        "username": username,
        "password_hash": password_hash
    }

def login_user(email: str, password: str):
    user = find_user_by_email(email)

    if user is None:
        return False, "User not found."

    if user["password_hash"] != hash_password(password):
        return False, "Incorrect password."

    return True, user