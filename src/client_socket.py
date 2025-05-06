import socket
import json

class ClientSocket:
    def __init__(self, host="localhost", port=9000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def send_request(self, request: dict) -> dict:
        self.sock.send(json.dumps(request).encode())
        data = self.sock.recv(8192).decode()
        return json.loads(data)

    def close(self):
        self.sock.close()
