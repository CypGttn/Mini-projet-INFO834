import re
import bcrypt
from bson.binary import Binary

class Connexion:
    def __init__(self, username, password, liste_user):
        self.connecte = False

        if re.match(r'^[^\d]+$', username) and re.match(r'^[^\d]+$', password):
            user = liste_user.find_one({"username": username})
            if user:
                hash_mdp = user['password']
                
                # Si le hash est stocké comme Binary, le convertir en bytes
                if isinstance(hash_mdp, Binary):
                    hash_mdp = bytes(hash_mdp)

                # Vérification du mot de passe
                if bcrypt.checkpw(password.encode('utf-8'), hash_mdp):
                    print("Connexion réussie !")
                    print(f"Bienvenue {username} !")
                    self.connecte = True
                    return

            print("Identifiant ou mot de passe incorrect.")
        else:
            print("Veuillez saisir deux chaînes de caractères.")
