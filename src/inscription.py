class Inscription : 
    def __init__(self, username, password, list_user):
         # Vérification que l'identifiant rentrer n'esxiste pas
        user = list_user.find_one({"username": username})
        if user : 
            self.add = False
        else : 
            conn = {"username": username, "password": password}
            list_user.insert_one(conn)
            
            self.add = True
            print(f"Bienvenu {username} !")
