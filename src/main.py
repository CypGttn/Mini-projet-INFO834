import argparse
from pymongo import MongoClient

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
        
        user = collection.find_one({"username": id_select})
        if id_select == user["username"] and mdp_select == user["password"]:
            print("Connexion réussie !")
            menu()
        else:
            print("Identifiant ou mot de passe incorrect.")
    elif selection == "2":
        id_select = input("Entrez l'identifiant que vous souhaitez utiliser : ")
        mdp_select = input("Entrez le mot de passe que vous souhaitez utiliser : ")
        
        print("Connexion réussie !")
        menu()
        
    
def menu():
    print(f"Bonjour, {id} !")
    print("Menu principal :")
    print("1. Consulter les messages")
    print("2. Envoyer un message ")
    print("3. Les membres connectés")
    
    selected = input ("Sélectionnez une option : ")
    
    if selected == "1":
        consulter_messages()
    elif selected == "2":
        envoyer_message()
    elif selected == "3":
        pers_connectés()
    
def consulter_messages():
    print("Voici vos messages :")
    # Afficher les messages ici
    pass

def envoyer_message():
    print("Envoyer un message :")
    # Logique pour envoyer un message ici
    pass

def pers_connectés():
    print("Voici les membres connectés :")
    # Afficher les membres connectés ici
    pass

if __name__ == "__main__":
    connexion()
