import smtplib
from email.message import EmailMessage

def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "crepykillcanal@gmail.com"
    msg['from'] = user
    pasword="3205283112h"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, pasword)
    server.send_message(msg)


    server.quit()

if __name__ == '__main__':
    email_alert("Test Alert", "This is a test", "jesus123quirozr01@gmail.com")