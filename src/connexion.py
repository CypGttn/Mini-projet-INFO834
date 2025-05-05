

class Connexion :
    def __init__ (self, username, password, liste_user):
        # On récupère les infos du user choisit avec id_select
        user = liste_user.find_one({"username": username})
        if username == user["username"] and password == user["password"]:
            print("Connexion réussie !")
            self.connecte=True
        else:
            print("Identifiant ou mot de passe incorrect.")
            
    