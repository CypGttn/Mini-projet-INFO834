import re


class Connexion :
    def __init__ (self, username, password, liste_user):
        self.connecte = False
        # On récupère les infos du user choisit avec id_select
        if re.match(r'^[^\d]+$', username) and re.match(r'^[^\d]+$', password):
            user = liste_user.find_one({"username": username})
            if username == user["username"] and password == user["password"]:
                print("Connexion réussie !")
                print(f"Bienvenue {username} !")
                self.connecte=True
            else:
                print("Identifiant ou mot de passe incorrect.")
        else : 
            print("Veuillez saisir deux chaînes de caractères.")
            
    