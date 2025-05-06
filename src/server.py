import socket
import threading
import json

class ServerSocket:
    def __init__(self, host='0.0.0.0', port=9000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))  # Écoute sur toutes les interfaces réseau (0.0.0.0)
        self.sock.listen(5)
        print(f"Serveur en écoute sur {host}:{port}")

    def accept_connections(self):
        while True:
            client_sock, client_addr = self.sock.accept()
            print(f"Connexion établie avec {client_addr}")
            threading.Thread(target=self.handle_client, args=(client_sock,)).start()

    def handle_client(self, client_sock):
        try:
            data = client_sock.recv(8192).decode()  # Lecture des données envoyées par le client
            request = json.loads(data)  # Conversion des données JSON
            print(f"Reçu du client : {request}")
            # Traite la requête du client ici...
            response = {"status": "OK", "message": "Requête reçue"}
            client_sock.send(json.dumps(response).encode())  # Envoie la réponse au client
        finally:
            client_sock.close()

if __name__ == "__main__":
    server = ServerSocket()
    server.accept_connections()
