from datetime import datetime
from utils.database import get_connection


def log_analysis(user, file_name, sessions_count, anomalies_count):
    username = user.get("username", "unknown") if user else "unknown"
    email = user.get("email", "unknown") if user else "unknown"

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO analysis_history (
                username,
                email,
                datetime,
                file_name,
                sessions_count,
                anomalies_count
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_name,
            sessions_count,
            anomalies_count
        ))

        connection.commit()