import argparse
from pymongo import MongoClient
from connexion import Connexion
from messages import Messages

#Se connecter à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
#COnnexion bdd
db = client['lesBellesMiches']

def connexion():
    print("Bienvenue dans Les Belles Miches ! Le chat qui fait gonfler ton temps d'écran. ")
    
    selection = input("Si vous souhaitez vous connectez, tapez 1. Si vous souhaitez créez un compte, tapez 2.")
    
    # Connexion avec la table 
    collection = db['user']
    
    if selection == "1":
        id_select = input("Entrez votre identifiant : ")
        mdp_select = input("Entrez votre mot de passe : ")
        connexion = Connexion(id_select, mdp_select, collection)   
        if connexion.connecte == True:
            print("Connexion réussie !")
            menu(id_select)
    
    elif selection == "2":
        id_select = input("Entrez l'identifiant que vous souhaitez utiliser : ")
        mdp_select = input("Entrez le mot de passe que vous souhaitez utiliser : ")
        
        # Vérification que l'identifiant rentrer n'esxiste pas
        user = collection.find_one({"username": id_select})
        if user : 
            print("Cet identifiant existe déjà.")
            connexion()
        else : 
            conn = {"username": id_select, "password": mdp_select}
            collection.insert_one(conn)
            
            print("Connexion réussie !")
            menu(id_select)

def menu(user):
    print(f"Bonjour, {user} !")
    print("Menu principal :")
    print("1. Consulter les messages")
    print("2. Envoyer un message ")
    print("3. Les membres connectés")
    
    selected = input ("Sélectionnez une option : ")
    
    messages = Messages(db, user)
    
    if selected == "1":
        consulter_messages(messages)
    elif selected == "2":
        envoyer_message(messages)
    elif selected == "3":
        pers_connectés()

def consulter_messages(messages : Messages):
    print("Voici vos messages que vous avez reçus :")
    recus = messages.received_messages()
    print(recus)
    
    for message in recus : 
        print(f"Sender {message['sender']}, Message : {message['text']}, Timestamp : {message['timestamp']}")
    

def envoyer_message(messages : Messages):
    print("Envoyer un message :")
    recipient = input("Entrez le nom d'utilisateur du destinataire : ")
    message = input("Entrez le message que vous sohuhaitez envoyer : ")
    messages.send_message(recipient, message)

def pers_connectés():
    print("Voici les membres connectés :")
    # Afficher les membres connectés ici
    pass

if __name__ == "__main__":
    connexion()
