import re
import bcrypt
from bson.binary import Binary

class Connexion:
    def __init__(self, username, password, liste_user):
        self.connecte = False

        # Vérifie que username et password sont bien des chaînes (ou bytes pour password)
        if isinstance(username, str) and isinstance(password, (str, bytes)) and \
           re.match(r'^[^\d]+$', username):

            print(f"Tentative de connexion pour : username='{username}'")

            user = liste_user.find_one({"username": username})
            if user:
                print("Utilisateur trouvé.")
                hash_mdp = user['password']

                # Convertir Binary BSON en bytes si nécessaire
                if isinstance(hash_mdp, Binary):
                    hash_mdp = bytes(hash_mdp)

                try:
                    # Encoder le mot de passe s'il est encore en string
                    password_bytes = password.encode('utf-8') if isinstance(password, str) else password

                    # Comparaison sécurisée
                    if bcrypt.checkpw(password_bytes, hash_mdp):
                        print("Connexion réussie !")
                        print(f"Bienvenue {username} !")
                        self.connecte = True
                        return
                    else:
                        print("Identifiant ou mot de passe incorrect.")
                except Exception as e:
                    print(f"Erreur lors de la vérification du mot de passe : {e}")
            else:
                print("Identifiant ou mot de passe incorrect.")
        else:
            print("Veuillez saisir un identifiant et un mot de passe valides (lettres uniquement, sans chiffres).")
