import datetime
import getpass
from bson import ObjectId
from bson.errors import InvalidId
from modules.connexion import Connexion
from modules.inscription import Inscription
from modules.messages import Messages
from modules.user_session_manager import UserSessionManager
from modules.requetes import Requetes

# Initialisation du gestionnaire de sessions
session_manager = UserSessionManager()


def connexion():
    print("Bienvenue dans Les Belles Miches ! Le chat qui fait gonfler ton temps d'écran.")
    selection = input("Tapez 1 pour vous connecter. Tapez 2 pour créer un compte. Tapez 3 pour arrêter le programme : ")
    collection = session_manager.users_collection

    if selection == "1":
        username = input("Entrez votre identifiant : ")
        password = getpass.getpass("Entrez votre mot de passe : ")
        user_id = session_manager.login_user(username, password)

        if user_id:
            print("Connexion réussie !")
            menu(username, user_id)
        else:
            print("Identifiants incorrects.")
            connexion()

    elif selection == "2":
        username = input("Choisissez un identifiant : ")
        password = input("Choisissez un mot de passe : ")
        inscr = Inscription(username, password, collection)

        if inscr.add:
            user = collection.find_one({"username": username})
            user_id = str(user["_id"])
            session_manager.log_event(user_id, "login")
            print("Inscription réussie !")
            menu(username, user_id)
        else:
            print("Cet identifiant existe déjà !")
            connexion()
    elif selection == "3":
        arret_programme_accueil()


def menu(username, user_id):
    print("Menu principal :")
    print("1. Consulter les messages")
    print("2. Envoyer un message")
    print("3. Voir les messages envoyés")
    print("4. Voir les connexions globales")
    print("5. Voir mes logs")
    print("6. Voir les utilisateurs connectés")
    print("7. Accéder aux requêtes avancées")
    print("8. Se déconnecter")
    print("9. Arrêter le programme")

    selected = input("Votre choix : ")
    messages = Messages(session_manager.db, username)

    if selected == "1":
        consulter_messages(messages)
    elif selected == "2":
        envoyer_message(messages)
    elif selected == "3":
        messages_envoyes(messages, username)
    elif selected == "4":
        session_manager.afficher_connexions_globales()
        user = session_manager.users_collection.find_one({"username": username})
        user_id = str(user["_id"])
        menu(username, user_id)
    elif selected == "5":
        session_manager.afficher_logs(user_id)
        user = session_manager.users_collection.find_one({"username": username})
        user_id = str(user["_id"])
        menu(username, user_id)
    elif selected == "6":
        afficher_utilisateurs_connectés(username)
    elif selected == "7":
        afficher_requetes(user_id, username)
    elif selected == "8":
        deconnexion(user_id, username)
        connexion()
    elif selected == "9":
        arret_programme(user_id, username)
    else:
        print("Option invalide.")

def consulter_messages(messages: Messages):
    print("Messages reçus :")
    try:
        recus = messages.received_messages_not_read()
        selected = input ("Lire les messages lus ? (y/n)")
        if selected=="y":
            messages.received_messages_read()
    except Exception as e:
        print(f"Erreur lors de la lecture des messages : {e}")
    user = session_manager.users_collection.find_one({"username": messages.username})
    user_id = str(user["_id"])
    menu(messages.username, user_id)

def envoyer_message(messages: Messages):
    destinataire = input("Nom du destinataire : ")
    contenu = input("Message : ")
    try:
        messages.send_message(destinataire, contenu)
        print("Message envoyé.")
    except Exception as e:
        print(f"Erreur lors de l'envoi : {e}")
    user = session_manager.users_collection.find_one({"username": messages.username})
    user_id = str(user["_id"])
    menu(messages.username, user_id)
    


def messages_envoyes(messages: Messages, username):
    print("Messages envoyés :")
    try:
        sent = messages.sent_messages(messages.username)
        if not sent:
            print("Vous n'avez envoyé aucun message.")
        else:
            for message in sent:
                print(f"À {message.get('recipient', 'Inconnu')} | {message.get('text', '')} | {message.get('timestamp', '')}")
    except Exception as e:
        print(f"Erreur lors de la récupération des messages envoyés : {e}")

    # Revenir au menu dans tous les cas
    user = session_manager.users_collection.find_one({"username": messages.username})
    user_id = str(user["_id"])
    menu(messages.username, user_id)



def afficher_utilisateurs_connectés(username):
    print("\nUtilisateurs connectés récemment :")
    redis_client = session_manager.redis_client
    users_collection = session_manager.users_collection

    for key in redis_client.scan_iter("user:*:events"):
        try:
            user_id = key.split(":")[1]
            events = redis_client.lrange(key, 0, 10)
            last_login = None
            last_logout = None

            for event in events:
                if event.startswith("login:"):
                    last_login = event.split("login:")[1]
                elif event.startswith("logout:"):
                    last_logout = event.split("logout:")[1]

            if last_login and (not last_logout or last_login > last_logout):
                user = users_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    print(f"- {user['username']} (ID: {user_id})")
        except (InvalidId, IndexError):
            continue

    
        
    user = users_collection.find_one({"username": username})
    user_id = str(user["_id"])
    menu(username, user_id)

def afficher_requetes(user_id, username):
    print("Voici quelques statistiques sur les dernières utilisations de l'application :")
    req = Requetes(session_manager.mongo_client, session_manager.redis_client)
    print(f"Nombre total d'utilisateurs : {str(req.total_users())}")
    user, val_conn = req.most_active_user()
    print(f"Utilisateur qui se connecte le plus est {user} avec {val_conn} connexions.")
    user, val_mess = req.most_messages_send()
    print(f"L'utilisateur qui envoie le plus de message est {user} avec {val_mess} messages envoyés.")
    user, val_mess = req.most_messages_receive()
    print(f"L'utilisateur qui reçoit le plus de message est {user} avec {val_mess} messages reçus.")

    user = session_manager.users_collection.find_one({"username": username})
    user_id = str(user["_id"])
    menu(username, user_id)    
    

def deconnexion(user_id, username):
    session_manager.logout_user(user_id)
    print("Vous avez été déconnecté !")
    
def arret_programme(user_id, username):
    deconnexion(user_id, username)
    print("Arret du programme")
    exit()
    
def arret_programme_accueil():
    print("Arret du programme")
    exit()
    
if __name__ == "__main__":
    connexion()

import datetime
import getpass
from bson import ObjectId
from bson.errors import InvalidId
from modules.connexion import Connexion
from modules.inscription import Inscription
from modules.messages import Messages
from modules.user_session_manager import UserSessionManager
from modules.requetes import Requetes

# Initialisation du gestionnaire de sessions
session_manager = UserSessionManager()


def connexion():
    print("Bienvenue dans Les Belles Miches ! Le chat qui fait gonfler ton temps d'écran.")
    selection = input("Tapez 1 pour vous connecter. Tapez 2 pour créer un compte. Tapez 3 pour arrêter le programme : ")
    collection = session_manager.users_collection

    if selection == "1":
        username = input("Entrez votre identifiant : ")
        password = getpass.getpass("Entrez votre mot de passe : ")
        user_id = session_manager.login_user(username, password)

        if user_id:
            print("Connexion réussie !")
            menu(username, user_id)
        else:
            print("Identifiants incorrects.")
            connexion()

    elif selection == "2":
        username = input("Choisissez un identifiant : ")
        password = input("Choisissez un mot de passe : ")
        inscr = Inscription(username, password, collection)

        if inscr.add:
            user = collection.find_one({"username": username})
            user_id = str(user["_id"])
            session_manager.log_event(user_id, "login")
            print("Inscription réussie !")
            menu(username, user_id)
        else:
            print("Cet identifiant existe déjà !")
            connexion()
    elif selection == "3":
        arret_programme_accueil()


def menu(username, user_id):
    print("Menu principal :")
    print("1. Consulter les messages")
    print("2. Envoyer un message")
    print("3. Voir les messages envoyés")
    print("4. Voir les connexions globales")
    print("5. Voir mes logs")
    print("6. Voir les utilisateurs connectés")
    print("7. Accéder aux requêtes avancées")
    print("8. Se déconnecter")
    print("9. Arrêter le programme")

    selected = input("Votre choix : ")
    messages = Messages(session_manager.db, username)

    if selected == "1":
        consulter_messages(messages)
    elif selected == "2":
        envoyer_message(messages)
    elif selected == "3":
        messages_envoyes(messages, username)
    elif selected == "4":
        session_manager.afficher_connexions_globales()
        user = session_manager.users_collection.find_one({"username": username})
        user_id = str(user["_id"])
        menu(username, user_id)
    elif selected == "5":
        session_manager.afficher_logs(user_id)
        user = session_manager.users_collection.find_one({"username": username})
        user_id = str(user["_id"])
        menu(username, user_id)
    elif selected == "6":
        afficher_utilisateurs_connectés(username)
    elif selected == "7":
        afficher_requetes(user_id, username)
    elif selected == "8":
        deconnexion(user_id, username)
        connexion()
    elif selected == "9":
        arret_programme(user_id, username)
    else:
        print("Option invalide.")

def consulter_messages(messages: Messages):
    print("Messages reçus :")
    try:
        recus = messages.received_messages_not_read()
        selected = input ("Lire les messages lus ? (y/n)")
        if selected=="y":
            messages.received_messages_read()
    except Exception as e:
        print(f"Erreur lors de la lecture des messages : {e}")
    user = session_manager.users_collection.find_one({"username": messages.username})
    user_id = str(user["_id"])
    menu(messages.username, user_id)

def envoyer_message(messages: Messages):
    destinataire = input("Nom du destinataire : ")
    contenu = input("Message : ")
    try:
        messages.send_message(destinataire, contenu)
        print("Message envoyé.")
    except Exception as e:
        print(f"Erreur lors de l'envoi : {e}")
    user = session_manager.users_collection.find_one({"username": messages.username})
    user_id = str(user["_id"])
    menu(messages.username, user_id)
    


def messages_envoyes(messages: Messages, username):
    print("Messages envoyés :")
    try:
        sent = messages.sent_messages(messages.username)
        if not sent:
            print("Vous n'avez envoyé aucun message.")
        else:
            for message in sent:
                print(f"À {message.get('recipient', 'Inconnu')} | {message.get('text', '')} | {message.get('timestamp', '')}")
    except Exception as e:
        print(f"Erreur lors de la récupération des messages envoyés : {e}")

    # Revenir au menu dans tous les cas
    user = session_manager.users_collection.find_one({"username": messages.username})
    user_id = str(user["_id"])
    menu(messages.username, user_id)



def afficher_utilisateurs_connectés(username):
    print("\nUtilisateurs connectés récemment :")
    redis_client = session_manager.redis_client
    users_collection = session_manager.users_collection

    for key in redis_client.scan_iter("user:*:events"):
        try:
            user_id = key.split(":")[1]
            events = redis_client.lrange(key, 0, 10)
            last_login = None
            last_logout = None

            for event in events:
                if event.startswith("login:"):
                    last_login = event.split("login:")[1]
                elif event.startswith("logout:"):
                    last_logout = event.split("logout:")[1]

            if last_login and (not last_logout or last_login > last_logout):
                user = users_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    print(f"- {user['username']} (ID: {user_id})")
        except (InvalidId, IndexError):
            continue

    
        
    user = users_collection.find_one({"username": username})
    user_id = str(user["_id"])
    menu(username, user_id)

def afficher_requetes(user_id, username):
    print("Voici quelques statistiques sur les dernières utilisations de l'application :")
    req = Requetes(session_manager.mongo_client, session_manager.redis_client)
    print(f"Nombre total d'utilisateurs : {str(req.total_users())}")
    user, val_conn = req.most_active_user()
    print(f"Utilisateur qui se connecte le plus est {user} avec {val_conn} connexions.")
    user, val_mess = req.most_messages_send()
    print(f"L'utilisateur qui envoie le plus de message est {user} avec {val_mess} messages envoyés.")
    user, val_mess = req.most_messages_receive()
    print(f"L'utilisateur qui reçoit le plus de message est {user} avec {val_mess} messages reçus.")

    user = session_manager.users_collection.find_one({"username": username})
    user_id = str(user["_id"])
    menu(username, user_id) 
    

def deconnexion(user_id, username):
    session_manager.logout_user(user_id)
    print("Vous avez été déconnecté !")
    
def arret_programme(user_id, username):
    deconnexion(user_id, username)
    print("Arret du programme")
    exit()
    
def arret_programme_accueil():
    print("Arret du programme")
    exit()
    
if __name__ == "__main__":
    connexion()
