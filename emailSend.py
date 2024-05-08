import smtplib
from email.message import EmailMessage

def send_email(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['to'] = to


    user = 'seniorsafe.uninorte@gmail.com'
    msg['From'] = user
    password = 'irusyktmrulzfoga'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()


if __name__ == '__main__':
    send_email('Test', 'Hola', 'jesus123quirozr01@gmail.com')

