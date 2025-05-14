import bcrypt

class Inscription:
    def __init__(self, username, password, liste_user):
        user = liste_user.find_one({"username": username})
        if user:
            self.add = False
            print("Nom d'utilisateur déjà pris.")
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            conn = {"username": username, "password": hashed}
            liste_user.insert_one(conn)
            self.add = True
            print(f"Bienvenue {username} !")