from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session
import datetime

from flask_socketio import SocketIO, send, join_room
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
            print("redirection to \menu")
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
        print("user_id not in session")
        return redirect(url_for('login'))
    username = session['username']
    print("rendering menu.html")
    return render_template('menu.html', username=username)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        sender_id = user_id
        recipient_username = request.form['recipient']
        text = request.form['message']

        recipient = db.user.find_one({"username": recipient_username})
        if not recipient:
            return "Utilisateur destinataire introuvable", 400

        message = {
            'sender': ObjectId(sender_id),
            'recipient': recipient["_id"],
            'text': text,
            'timestamp': datetime.datetime.utcnow(),
            'read': False
        }
        db.message.insert_one(message)

        # Emission du message en temps réel
        sender = db.user.find_one({'_id': ObjectId(sender_id)})
        socketio.emit('new_message', {
            'sender': sender["username"],
            'text': text,
            'timestamp': message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })

        return redirect(url_for('messages'))

    received_messages = db.message.find({'recipient': ObjectId(user_id)})
    enriched_messages = []
    for msg in received_messages:
        sender = db.user.find_one({'_id': msg['sender']})
        enriched_messages.append({
            'sender': sender['username'],
            'text': msg['text'],
            'timestamp': msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('messages.html', messages=enriched_messages)
@app.route('/logout')
def logout():
    session.clear()  # ou ton système de session personnalisé
    return redirect(url_for('login'))

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        join_room(str(user_id))

@socketio.on('message')
def handle_message(msg):
    print('Message reçu: ' + msg)
    send(msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
