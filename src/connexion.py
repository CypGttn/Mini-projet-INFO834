import re
import bcrypt

class Connexion:
    def __init__(self, username, password, liste_user):
        self.connecte = False

        if re.match(r'^[^\d]+$', username) and re.match(r'^[^\d]+$', password):
            user = liste_user.find_one({"username": username})
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                print("Connexion réussie !")
                print(f"Bienvenue {username} !")
                self.connecte = True
            else:
                print("Identifiant ou mot de passe incorrect.")
        else:
            print("Veuillez saisir deux chaînes de caractères.")