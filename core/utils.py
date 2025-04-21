from flask_mail import Message
from core import mail

def send_email(name, email, score):
    subject = "⚠️ Academic Alert: Low Performance"
    body = f"""
    Dear {name},

    We noticed your recent performance shows a low score of {score:.2f} in Semester 3.

    Please meet your academic advisor to get assistance and improve your performance.

    Best regards,
    Academic Support Team
    """

    msg = Message(subject=subject, recipients=[email], body=body)
    mail.send(msg)
