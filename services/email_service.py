import os
import smtplib
from pathlib import Path
from email.message import EmailMessage

from dotenv import load_dotenv


def send_email_report(recipient_email, report_path, language="uk"):
    load_dotenv()

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_server, smtp_email, smtp_password]):
        return False, "SMTP settings are not configured."

    report_path = Path(report_path)

    if not report_path.exists():
        return False, "Report file not found."

    if language == "en":
        subject = "User Behavior Analysis Report"
        body = "Hello,\n\nYour user behavior analysis report is attached.\n\nBest regards,\nUser Behavior Analysis App"
    else:
        subject = "Звіт аналізу поведінки користувача"
        body = "Вітаємо,\n\nВаш звіт аналізу поведінки користувача додано у вкладенні.\n\nЗ повагою,\nЗастосунок аналізу поведінки користувачів"

    message = EmailMessage()
    message["From"] = smtp_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.set_content(body)

    with open(report_path, "rb") as file:
        message.add_attachment(
            file.read(),
            maintype="text",
            subtype="plain",
            filename=report_path.name
        )

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(message)

        return True, "Email sent successfully."

    except Exception as e:
        return False, f"Email sending error: {e}"