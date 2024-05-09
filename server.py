from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from paswords import ACOUNT_SID, AUTH_TOKEN, HOST, USER, PASSWORD, DATABASE, EMAIL_USER, EMAIL_PASSWORD
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Genera una clave secreta aleatoria de 16 bytes (32 caracteres hexadecimales)

actions = []
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'gif'}

account_sid = ACOUNT_SID
auth_token = AUTH_TOKEN
client = Client(account_sid, auth_token)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # El puerto para el servidor SMTP

import mysql.connector

# Create a connection to the database
db = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)

cursor = db.cursor()

# Función para enviar correos electrónicos
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        print("Correo electrónico enviado correctamente a", to_email)
    except Exception as e:
        print("Error al enviar el correo electrónico:", str(e))

# Lista en memoria para almacenar los destinatarios de alertas
def get_destinatarios_alerta():
    if 'destinatarios_alerta' not in session:
        session['destinatarios_alerta'] = []
    return session['destinatarios_alerta']

# Ruta para registrar nuevos destinatarios de alertas
@app.route('/registrar_destinatario', methods=['POST'])
def registrar_destinatario():
    if request.json and 'email' in request.json:
        email = request.json['email']
        print(email)
        destinatarios_alerta = get_destinatarios_alerta()
        destinatarios_alerta.append(email)
        session.modified = True
        print(session)  # Marcar la sesión como modificada
        return redirect(url_for('monitoreo_acciones'))
    else:
        return 'Solicitud incorrecta.', 400

# Ruta para salir de la lista de destinatarios de alertas
@app.route('/salir_de_alertas', methods=['POST'])
def salir_de_alertas():
    if 'destinatarios_alerta' in session:
        print(1)
        email = session['destinatarios_alerta']
        print(email)
        destinatarios_alerta = get_destinatarios_alerta()
        print(destinatarios_alerta)
        if email == destinatarios_alerta:
            destinatarios_alerta.remove(email[0])
            session.modified = True
            print(destinatarios_alerta)
            if not destinatarios_alerta:
                session.pop('destinatarios_alerta', None)
                print(session)
    return redirect(url_for('pagina_principal'))

# Función para enviar alertas de caída
def enviar_alerta_de_caída():
    asunto = 'Alerta de Caída'
    cuerpo = 'Se ha detectado una caída. Por favor, verifique el estado de la persona.'
    destinatarios_alerta = get_destinatarios_alerta()
    for destinatario in destinatarios_alerta:
        print(destinatario)
        send_email(destinatario, asunto, cuerpo)

# Ruta para la página de configuración de alertas
@app.route('/configuracion_alertas')
def configuracion_alertas():
    return render_template('configuracion_alertas.html')

# Ruta de la página principal
@app.route('/')
def pagina_principal():
    return render_template('lpage.html')

# Ruta para manejar la consulta de históricos
@app.route('/consultar_historicos', methods=['POST'])
def consultar_historicos():
    if request.method == 'POST':
        # Obtener las fechas de inicio y fin del formulario
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        accion = request.form.get('accion')  # Obtener la acción seleccionada
        
        # Construir la consulta SQL con el filtro de acción
        if accion:
            query = "SELECT fecha, accion FROM registro WHERE fecha BETWEEN %s AND %s AND accion = %s ORDER BY fecha DESC"
            cursor.execute(query, (fecha_inicio, fecha_fin, accion))
        else:
            query = "SELECT fecha, accion FROM registro WHERE fecha BETWEEN %s AND %s ORDER BY fecha DESC"
            cursor.execute(query, (fecha_inicio, fecha_fin))

        resultados = cursor.fetchall()

        # Devolver los resultados como JSON
        return jsonify({'resultados': resultados})
    else:
        return 'Método de solicitud no permitido.', 405

# Ruta para cargar la página de consulta de históricos
@app.route('/historicos')
def historicos():
    return render_template('historicos.html')

@app.route('/index')
def monitoreo_acciones():
    return render_template('index.html', actions=actions)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get_actions')
def get_actions():
    # Devuelve las últimas dos acciones como JSON
    return jsonify({'actions': actions[-2:]})

@app.route('/upload', methods=['POST'])
def gifreceived():
    if 'file' in request.files:
        # Handle the receipt of GIF files
        file = request.files['file']
        file.save('static/received.gif')
        return 'GIF file received correctly.' 

@app.route('/receive_data', methods=['POST'])
def receive_data():    
    if request.json and 'action' in request.json and 'date' in request.json:
        # Handle the receipt of predicted actions in JSON format
        action = request.json['action']
        if action == 'Alerta de Caida':
            message = client.messages.create(
                from_='+16146109328',
                body='Alerta de Caida por favor verifique el estado de la persona. http://seniorsafe.ddns.net',
                to='+573003887981'
            )
            destinatarios_alerta = get_destinatarios_alerta()
            print(destinatarios_alerta)
            send_email(destinatarios_alerta, 'Alerta de Caída', 'Alerta de Caida por favor verifique el estado de la persona. http://seniorsafe.ddns.net')

            print(message.sid)
        date = request.json['date']
        actions.append({'action': action, 'date': date})

        # Insert the action and date into the database
        query = "INSERT INTO registro (fecha, accion) VALUES (%s, %s)"
        values = (date, action)
        cursor.execute(query, values)
        db.commit()

        return 'Action and date received correctly.'
    else:
        return 'Incorrect request.', 400

@app.route('/last_fall_date')
def last_fall_date():
    print(session)
    # Query the database for the latest fall action
    query = "SELECT fecha FROM registro WHERE accion = 'Alerta de Caida' ORDER BY fecha DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()

    # If a fall action exists, return the date
    if result:
        return jsonify({'last_fall_date': result[0]})
    else:
        return 'No fall action found.', 404

@app.route('/research')
def research():
    return render_template('research.html')

@app.route('/registro')
def registro():
    return render_template('register.html')

from flask import make_response

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
