import argparse

def connexion():
    print("Bienvenue dans Les Belles Miches ! Le chat qui fait gonfler ton temps d'écran. ")
    
    selection = input("Si vous souhaitez vous connectez, tapez 1. Si vous souhaitez créez un compte, tapez 2.")
    
    id = "angele"
    mdp = "brol"
    
    if selection == "1":
        id_select = input("Entrez votre identifiant : ")
        mdp_select = input("Entrez votre mot de passe : ")
        if id_select == id and mdp_select == mdp:
            print("Connexion réussie !")
            print(f"Bonjour, {id} !")
        else:
            print("Identifiant ou mot de passe incorrect.")
    elif selection == "2":
        id_select = input("Entrez l'identifiant que vous souhaitez utiliser : ")
        mdp_select = input("Entrez le mot de passe que vous souhaitez utiliser : ")
        
        print("Connexion réussie !")
        print(f"Bonjour, {id} !")
    

if __name__ == "__main__":
    connexion()
