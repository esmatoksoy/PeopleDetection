#Raspberry Pi People Counting and Daily Report System

This project uses a Raspberry Pi and a camera to detect and count people entering a space in real-time. It tracks visit durations and generates daily summary graphs showing people flow patterns. At the end of each day, it automatically emails the report to the user.

The system is built with Python, using computer vision libraries for detection, and integrates data logging, graph generation, and email notifications.

Features
Real-time people counting with a Raspberry Pi camera

Tracking of individual visit durations

Daily generation of visit summary graphs

Automated email reports sent daily to a configured email address

Create a .env file in the project root to securely store your email credentials and settings:

EMAIL_USER=your_email@gmail.com

EMAIL_PASSWORD=your_email_password_or_app_password

EMAIL_RECEIVER=recipient_email@gmail.com
