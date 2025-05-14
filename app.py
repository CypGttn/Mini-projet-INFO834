from bson import ObjectId
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import datetime
import logging

from flask_socketio import SocketIO, emit, send, join_room
from pymongo import MongoClient
import redis
from modules.connexion import Connexion
from modules.inscription import Inscription
from modules.user_session_manager import UserSessionManager
from modules.messages import Messages
from modules.requetes import Requetes

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Remplace avec une clé secrète aléatoire pour ta session
socketio = SocketIO(app)

# Connexion à MongoDB et Redis
mongo_client = MongoClient()
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

        session_manager.login_user(username, password)

        # Recherche de l'utilisateur dans la base
        user = db.user.find_one({'username': username})
        if user:
            # On vide toute session précédente pour éviter des collisions
            session.clear()

            # On sauvegarde les infos utiles dans la session
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']

            return redirect(url_for('chat'))
        else:
            return 'Nom d’utilisateur ou mot de passe incorrect', 401

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

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    username = session['username']

    users = list(db.user.find({'_id': {'$ne': user_id}}))  # tous les autres
    return render_template('chat.html', users=users, user_id=str(user_id), username=username)

@app.route('/messages_with/<user_id>')
def messages_with(user_id):
    if 'user_id' not in session:
        return jsonify([])

    current_user = ObjectId(session['user_id'])
    other_user = ObjectId(user_id)

    messages = list(db.message.find({
        '$or': [
            {'sender': current_user, 'recipient': other_user},
            {'sender': other_user, 'recipient': current_user}
        ]
    }).sort('timestamp', 1))

    result = []
    for m in messages:
        sender_doc = db.user.find_one({'_id': m['sender']})
        result.append({
            'sender': sender_doc['username'],
            'text': m['text'],
            'timestamp': m['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            'sender_id': str(m['sender']),
            'recipient_id': str(m['recipient'])
        })

    return jsonify(result)


@app.route('/stats')
def stats():
    if 'username' not in session:
        return redirect(url_for('login'))

    req = Requetes(session_manager.mongo_client, session_manager.redis_client)
    total_users = req.total_users()
    most_active_user, active_count = req.most_active_user()
    top_sender, sent_count = req.most_messages_send()
    top_receiver, recv_count = req.most_messages_receive()

    return render_template('stats.html', 
                           username=session['username'],
                           total_users=total_users,
                           most_active_user=most_active_user,
                           active_count=active_count,
                           top_sender=top_sender,
                           sent_count=sent_count,
                           top_receiver=top_receiver,
                           recv_count=recv_count)

@app.route('/logout')
def logout():
    session.clear()  # ou ton système de session personnalisé
    return redirect(url_for('login'))

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        join_room(str(user_id))
        print(f"[SOCKET] Utilisateur connecté : {user_id} rejoint la room {user_id}")
    else:
        print("[SOCKET] Connexion sans session utilisateur")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id:
        print(f"[SOCKET] Déconnexion de l'utilisateur : {user_id}")

@socketio.on('load_messages')
def load_messages(recipient_id):
    sender_id = session.get('user_id')
    if not sender_id:
        return

    # Récupère les messages entre les deux utilisateurs
    messages = db.message.find({
        '$or': [
            {'sender': ObjectId(sender_id), 'recipient': ObjectId(recipient_id)},
            {'sender': ObjectId(recipient_id), 'recipient': ObjectId(sender_id)}
        ]
    }).sort('timestamp', 1)

    formatted_messages = []
    for msg in messages:
        sender_doc = db.user.find_one({'_id': msg['sender']})
        formatted_messages.append({
            'sender_name': sender_doc['username'],
            'text': msg['text'],
            'timestamp': msg['timestamp'].strftime('%H:%M %d/%m')
        })

    emit('load_history', formatted_messages)

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = ObjectId(session['user_id'])
    recipient_id = ObjectId(data['recipient_id'])
    text = data['text']

    if not sender_id or not recipient_id or not text:
        return
    
    sender_doc = db.user.find_one({'_id': sender_id})
    timestamp = datetime.datetime.utcnow()

    message = {
        'sender': sender_id,
        'recipient': recipient_id,
        'text': text,
        'timestamp': timestamp,
        'read': False
    }
    db.message.insert_one(message)


    msg_data = {
        'sender': sender_doc['username'],
        'text': data['text'],
        'timestamp': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        'sender_id': str(sender_id),
        'recipient_id': str(recipient_id)
    }

    # Envoyer à la room du destinataire et de l'expéditeur
    emit('new_message', msg_data, room=str(recipient_id))
    emit('new_message', msg_data, room=str(sender_id))


@socketio.on('message')
def handle_message(msg):
    print('Message reçu: ' + msg)
    send(msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
