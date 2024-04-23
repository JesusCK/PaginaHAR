from flask import Flask, render_template, request, jsonify
import os
app = Flask(__name__)

actions = []
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get_actions')
def get_actions():
    # Devuelve las últimas dos acciones como JSON
    return jsonify({'actions': actions[-2:]})
import mysql.connector

# Create a connection to the database
db = mysql.connector.connect(
    host="humandetectdb.col4pixfadqv.us-east-2.rds.amazonaws.com",
    user="admin",
    password="123456789",
    database="HumanActionsRecognitions"
)

cursor = db.cursor()

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if 'file' in request.files:
        # Handle the receipt of GIF files
        file = request.files['file']
        file.save('static/received.gif')
        return 'GIF file received correctly.'
    elif request.json and 'action' in request.json and 'date' in request.json:
        # Handle the receipt of predicted actions in JSON format
        action = request.json['action']
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
    

@app.route('/')
def index():
    return render_template('index.html', actions=actions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    

