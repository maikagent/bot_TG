import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = 'smtp.ratymaty@yandex.ru'
SMTP_PORT = 587
EMAIL = 'ratymaty@yandex.ru'
PASSWORD = 'Lexp4908qc'

def send_email(user_id, vehicle_number, vehicle_brand, is_guest, request_date):
    subject = "Подтверждение заявки"
    body = f"""
    Заявка подтверждена!
    Номер авто: {vehicle_number}
    Марка авто: {vehicle_brand}
    Статус: {is_guest}
    Дата заявки: {request_date}
    """
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = 'ing1@winzavod.ru'  # Поменяйте на email получателя
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, [msg['To']], msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
