from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from twilio.rest import Client
from paswords import ACOUNT_SID, AUTH_TOKEN, HOST, USER, PASSWORD, DATABASE
app = Flask(__name__)

actions = []
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'gif'}

account_sid = ACOUNT_SID
auth_token = AUTH_TOKEN
client = Client(account_sid, auth_token)

import mysql.connector

# Create a connection to the database
db = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)

cursor = db.cursor()

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
def index2():
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
    # Query the database for the latest fall action
    query = "SELECT fecha FROM registro WHERE accion = 'Alerta de Caida' ORDER BY fecha DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()

    # If a fall action exists, return the date
    if result:
        return jsonify({'last_fall_date': result[0]})
    else:
        return 'No fall action found.', 404
@app.route('/')
def index():
    return render_template('lpage.html')

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

@app.route('/ingreso', methods=['POST'])
def ingreso():
    if request.json and 'email' in request.json and 'password' in request.json:
        email = request.json['email']
        password = request.json['password']
        
        # Process the received email and password data
        # ...
        print(email, password)
        return redirect(url_for('historicos'))  # Redirect to the index2 page
    else:
        return 'Incorrect request.', 400
    # Consulta para obtener todas las acciones y fechas desde el inicio hasta el último dato recibido


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

    

