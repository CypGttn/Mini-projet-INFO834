import datetime
import redis
from bson import ObjectId
from pymongo import MongoClient
from connexion import Connexion
from inscription import Inscription
from messages import Messages
from bson.errors import InvalidId

# Connexions MongoDB et Redis
client = MongoClient('mongodb://localhost:27017/')
db = client['lesBellesMiches']
users_collection = db['user']
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def log_event(user_id, event_type):
    timestamp = datetime.datetime.now().isoformat()
    event = f"{event_type}:{timestamp}"
    redis_client.lpush(f"user:{user_id}:events", event)

    if event_type == "login":
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            username = user.get("username")
            redis_client.lpush("global:events", f"User {username} logged in at {timestamp}")
    print(f"Utilisateur {user_id} {event_type} à {timestamp}")

def afficher_logs(user_id):
    logs = redis_client.lrange(f"user:{user_id}:events", 0, 9)
    if logs:
        print("\nDerniers logs :")
        for log in logs:
            print(log)
    else:
        print("Aucun log trouvé.")

def afficher_connexions_globales():
    logs = redis_client.lrange("global:events", 0, 9)
    if logs:
        print("\nDernières connexions globales :")
        for log in logs:
            print(log)
    else:
        print("Aucune connexion globale trouvée.")

def afficher_utilisateurs_connectés():
    print("\nUtilisateurs connectés récemment :")
    connected_users = set()

    for key in redis_client.scan_iter("user:*:events"):
        user_id = key.split(":")[1]
        events = redis_client.lrange(key, 0, 10)

        last_login_index = next((i for i, ev in enumerate(events) if ev.startswith("login")), -1)
        last_logout_index = next((i for i, ev in enumerate(events) if ev.startswith("logout")), -1)

        if 0 <= last_login_index < last_logout_index or last_login_index == -1:
            continue

        try:
            obj_id = ObjectId(user_id)
            user = users_collection.find_one({"_id": obj_id})
            if user:
                print(f"- {user.get('username')} (ID: {user_id})")
                connected_users.add(user_id)
        except InvalidId:
            continue  # Ignore les IDs invalides venant de Redis

    if not connected_users:
        print("Aucun utilisateur connecté actuellement.")


def connexion():
    print("Bienvenue dans Les Belles Miches ! Le chat qui fait gonfler ton temps d'écran.")

    selection = input("Tapez 1 pour vous connecter. Tapez 2 pour créer un compte : ")

    if selection == "1":
        username = input("Entrez votre identifiant : ")
        password = input("Entrez votre mot de passe : ")
        user = users_collection.find_one({"username": username})

        if user and user.get("password") == password:
            user_id = str(user["_id"])
            log_event(user_id, "login")
            print("Connexion réussie !")
            menu(username, user_id)
        else:
            print("Identifiants incorrects.")
            connexion()

    elif selection == "2":
        username = input("Choisissez un identifiant : ")
        password = input("Choisissez un mot de passe : ")

        if users_collection.find_one({"username": username}):
            print("Cet identifiant existe déjà.")
            connexion()
        else:
            new_id = users_collection.insert_one({"username": username, "password": password}).inserted_id
            log_event(str(new_id), "login")
            print("Inscription réussie !")
            menu(username, str(new_id))

def menu(username, user_id):
    while True:
        print(f"\nBonjour, {username} !")
        print("Menu principal :")
        print("1. Consulter les messages")
        print("2. Envoyer un message")
        print("3. Voir les messages envoyés")
        print("4. Voir les connexions globales")
        print("5. Voir mes logs")
        print("6. Se déconnecter")
        print("7. Voir les utilisateurs connectés")

        selected = input("Votre choix : ")
        messages = Messages(db, username)

        if selected == "1":
            consulter_messages(messages)
        elif selected == "2":
            envoyer_message(messages)
        elif selected == "3":
            messages_envoyés(messages)
        elif selected == "4":
            afficher_connexions_globales()
        elif selected == "5":
            afficher_logs(user_id)
        elif selected == "6":
            log_event(user_id, "logout")
            print("Déconnexion réussie.")
            break
        elif selected == "7":
            afficher_utilisateurs_connectés()
        else:
            print("Option invalide.")

def consulter_messages(messages: Messages):
    print("Messages reçus :")
    try:
        recus = messages.received_messages()
        if not recus:
            print("Aucun message reçu.")
            return
        for message in recus:
            print(f"De {message.get('sender', 'Inconnu')} | {message.get('text', '')} | {message.get('timestamp', '')}")
    except Exception as e:
        print(f"Erreur lors de la lecture des messages : {e}")

def envoyer_message(messages: Messages):
    destinataire = input("Nom du destinataire : ")
    contenu = input("Message : ")
    try:
        messages.send_message(destinataire, contenu)
        print("Message envoyé.")
    except Exception as e:
        print(f"Erreur lors de l'envoi : {e}")

def messages_envoyés(messages: Messages):
    print("Messages envoyés :")
    try:
        sent = messages.sent_messages(messages.username)
        if not sent:
            print("Vous n'avez envoyé aucun message.")
            return
        for message in sent:
            print(f"À {message.get('recipient', 'Inconnu')} | {message.get('text', '')} | {message.get('timestamp', '')}")
    except Exception as e:
        print(f"Erreur lors de la récupération des messages envoyés : {e}")

if __name__ == "__main__":
    connexion()
