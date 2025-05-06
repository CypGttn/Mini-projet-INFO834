import socket
import json

class ClientSocket:
    def __init__(self, host="10.7.178.239", port=9000):  # Utilise l'IP du serveur ici
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))  # Connexion au serveur via l'IP et le port

    def send_request(self, request: dict) -> dict:
        self.sock.send(json.dumps(request).encode())  # Envoie la requête en JSON
        data = self.sock.recv(8192).decode()  # Réception de la réponse
        return json.loads(data)  # Retourne la réponse sous forme de dictionnaire

    def close(self):
        self.sock.close()
