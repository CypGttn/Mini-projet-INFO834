from flask import Flask, render_template, request, redirect, url_for, session
import datetime

from flask_socketio import SocketIO, send
from pymongo import MongoClient
import redis
from modules.connexion import Connexion
from modules.inscription import Inscription
from modules.user_session_manager import UserSessionManager
from modules.messages import Messages

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Remplace avec une clé secrète aléatoire pour ta session
socketio = SocketIO(app)

# Connexion à MongoDB et Redis
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["lesBellesMiches"]
users_collection = db["user"]

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

session_manager = UserSessionManager(mongo_uri="mongodb://localhost:27017/", redis_host="localhost", redis_port=6379)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_id = session_manager.login_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('menu'))
        else:
            return "Identifiants incorrects", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        inscr = Inscription(username, password, users_collection)

        if inscr.add:
            return redirect(url_for('login'))
        else:
            return "L'identifiant existe déjà", 400

    return render_template('register.html')

@app.route('/menu')
def menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    username = session['username']
    return render_template('menu.html', username=username)

@app.route('/messages', methods=['GET'])
def messages_display():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    received_messages = db.messages.find({'receiver': user_id})
    return render_template('messages_display.html', messages=received_messages or [])

app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        sender_id = session.get('user_id')
        recipient = request.form['recipient']
        text = request.form['message']

        if not sender_id or not recipient or not text:
            return "Champs manquants", 400

        message = {
            'sender': sender_id,
            'receiver': recipient,
            'text': text,
            'timestamp': datetime.datetime.utcnow(),
            'read': False
        }
        db.messages.insert_one(message)
        return redirect(url_for('messages_display'))

    # GET request: afficher le formulaire pour envoyer un message
    return render_template('send_message.html')

@app.route('/logout')
def logout():
    session.clear()  # ou ton système de session personnalisé
    return redirect(url_for('login'))

@socketio.on('message')
def handle_message(msg):
    print('Message reçu: ' + msg)
    send(msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
