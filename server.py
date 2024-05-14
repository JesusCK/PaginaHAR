from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from paswords import ACOUNT_SID, AUTH_TOKEN, HOST, USER, PASSWORD, DATABASE, EMAIL_USER, EMAIL_PASSWORD
import secrets
from flask_session import Session
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Genera una clave secreta aleatoria de 16 bytes (32 caracteres hexadecimales)
app.config['SESSION_TYPE'] = 'filesystem'  # Puedes usar 'redis' o 'sqlalchemy' si lo prefieres
app.config['SESSION_FILE_DIR'] = './flask_session/'  # Directorio donde se almacenarán las sesiones en el sistema de archivos
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'

# Inicializa la extensión de sesión
Session(app)
destinatario = []
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
        print('paso por aqui')
        session['destinatarios_alerta'] = []
    return session['destinatarios_alerta']

# Ruta para registrar nuevos destinatarios de alertas
@app.route('/registrar_destinatario', methods=['POST'])
def registrar_destinatario():
    if request.json and 'email' in request.json:
        email = request.json['email']
        print(email)
        session['email'] = email
        session.modified = True
        print(f'{session} estan activas') 
    # Marcar la sesión como modificada
        return redirect(url_for('monitoreo_acciones'))
    else:
        return 'Solicitud incorrecta.', 400

# Ruta para salir de la lista de destinatarios de alertas
@app.route('/salir_de_alertas', methods=['POST'])
def salir_de_alertas():
    if 'email' in session:
        print(1)
        email = session['email']
        session.pop('email', None)
        print(session)
        session.modified = True
        
        
    return redirect(url_for('pagina_principal'))

# Función para enviar alertas de caída

def enviar_alerta_de_caída(email):
    asunto = 'Alerta de Caída'
    cuerpo = 'Se ha detectado una caída. Por favor, verifique el estado de la persona. http://seniorsafe.ddns.net/index'
    print("enviar alerta de caida")
    
    send_email(email, asunto, cuerpo)
    print("enviado")

# Ruta para la página de configuración de alertas
@app.route('/configuracion_alertas')
def configuracion_alertas():
    return render_template('configuracion_alertas.html')

# Ruta de la página principal
@app.route('/')
def pagina_principal():
    return render_template('lpage.html')

@app.route('/prueba')
def prueba():
    return render_template('prueba.html')

# Ruta para manejar la consulta de históricos
@app.route('/consultar_historicos', methods=['POST'])
def consultar_historicos():
    if request.method == 'POST':
        # Obtener las fechas de inicio y fin del formulario
        datetimes = request.form['datetimes']
        fecha_inicio, fecha_fin = datetimes.split(' - ')
        #fecha_inicio += ':00'
        #fecha_fin += ':00'
        
        
        # Convertir las fechas de inicio y fin a formato datetime
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M')
        fecha_inicio = fecha_inicio.strftime('%y-%m-%dT%H:%M')
        fecha_fin = fecha_fin.strftime('%y-%m-%dT%H:%M')
        #print(datetimes)
        print(fecha_inicio)

        
        # fecha_inicio = request.form['fecha_inicio']
        # fecha_fin = request.form['fecha_fin']
        accion = request.form.get('accion')  # Obtener la acción seleccionada
        #print(datetimes)
        print(fecha_inicio)
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
        

        date = request.json['date']
        actions.append({'action': action, 'date': date})

        # Insert the action and date into the database
        query = "INSERT INTO registro (fecha, accion) VALUES (%s, %s)"
        values = (date, action)
        cursor.execute(query, values)
        db.commit()

        if action == 'Alerta de Caída':
            
            email = session['email']
            enviar_alerta_de_caída(email)
            print('Alerta de caída enviada a', email)

        return 'Action and date received correctly.'
    else:
        return 'Incorrect request.', 400



@app.route('/check_session')
def check_session():
    if 'email' in session:
        return f"Email en la sesión: {session['email']}"
    else:
        return "No hay email en la sesión."
    
@app.route('/enviar_email', methods=['POST'])
def enviar_email():
    if request.json and 'email' in session:
        email = session['email']
        action = request.json['action']
        if action == 'Alerta de Caída':
            asunto = "Alerta de Caída"
            cuerpo = "Se ha detectado una caída. Por favor, verifique el estado de la persona. http://seniorsafe.ddns.net/index"
            send_email(email, asunto, cuerpo)
            return f"Correo electrónico enviado correctamente a {email}"
        else:
            return "Acción no válida.", 400
    else:
        return "No hay correo o alerta de caida", 400

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

@app.route('/login')
def login():
    return render_template('login.html')

from flask import make_response
from datetime import datetime

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
