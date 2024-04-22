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

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if 'file' in request.files:
        # Manejar la recepción de archivos GIF
        file = request.files['file']
        file.save('static/received.gif')
        return 'Archivo GIF recibido correctamente.'
    elif request.json and 'action' in request.json:
        # Manejar la recepción de acciones predichas en formato JSON
        action = request.json['action']
        actions.append(action)
        return 'Acción recibida correctamente.'
    else:
        return 'Solicitud incorrecta.', 400
    

@app.route('/')
def index():
    return render_template('index.html', actions=actions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    

