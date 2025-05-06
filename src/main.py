from client_socket import ClientSocket
import getpass

def connexion():
    print("Bienvenue dans Les Belles Miches (v2 Socket)")

    sock = ClientSocket()
    while True:
        sel = input("1. Connexion | 2. Inscription (non dispo) > ")
        if sel == "1":
            username = input("Identifiant : ")
            password = getpass.getpass("Mot de passe : ")

            res = sock.send_request({"action": "login", "username": username, "password": password})
            if res.get("status") == "ok":
                print("✅ Connecté.")
                menu(sock, username)
                break
            else:
                print("❌ Erreur de connexion.")
        else:
            print("Inscription non implémentée ici.")

def menu(sock, username):
    while True:
        print("\nMenu")
        print("1. Voir messages")
        print("2. Envoyer un message")
        print("3. Se déconnecter")
        sel = input("> ")

        if sel == "1":
            res = sock.send_request({"action": "get_messages", "username": username})
            for m in res.get("messages", []):
                print(f"{m['from']} > {m['message']} ({m['timestamp']})")

        elif sel == "2":
            to = input("Destinataire : ")
            msg = input("Message : ")
            sock.send_request({"action": "send", "from": username, "to": to, "message": msg})

        elif sel == "3":
            sock.send_request({"action": "logout", "username": username})
            sock.close()
            print("Déconnecté.")
            break

if __name__ == "__main__":
    connexion()
