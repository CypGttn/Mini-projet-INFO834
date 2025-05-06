import socket
import threading
import json
import datetime
import redis
from pymongo import MongoClient

mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["lesBellesMiches"]
users_collection = db["user"]
messages_collection = db["messages"]
redis_client = redis.Redis(decode_responses=True)

clients = {}

def handle_client(conn, addr):
    username = None
    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            request = json.loads(data)
            response = {}

            if request["action"] == "login":
                user = users_collection.find_one({"username": request["username"]})
                if user and user["password"] == request["password"]:
                    username = request["username"]
                    clients[username] = conn
                    log_event(user["_id"], "login", username)
                    response["status"] = "ok"
                else:
                    response["status"] = "error"
                    response["message"] = "Identifiants incorrects."

            elif request["action"] == "send":
                sender = request["from"]
                to = request["to"]
                msg = request["message"]
                messages_collection.insert_one({
                    "from": sender, "to": to, "message": msg, "timestamp": datetime.datetime.now(), "read": False
                })
                if to in clients:
                    clients[to].send(json.dumps({"from": sender, "message": msg}).encode())
                response["status"] = "sent"

            elif request["action"] == "get_messages":
                user = request["username"]
                results = list(messages_collection.find({"to": user}))
                for m in results:
                    m["_id"] = str(m["_id"])
                    m["timestamp"] = m["timestamp"].isoformat()
                response["messages"] = results

            elif request["action"] == "logout":
                user = users_collection.find_one({"username": username})
                if user:
                    log_event(user["_id"], "logout", username)
                response["status"] = "logged_out"
                break

            conn.send(json.dumps(response).encode())
    except Exception as e:
        print(f"Erreur avec {addr} : {e}")
    finally:
        if username in clients:
            del clients[username]
        conn.close()

def log_event(user_id, event_type, username):
    timestamp = datetime.datetime.now().isoformat()
    redis_client.lpush(f"user:{user_id}:events", f"{event_type}:{timestamp}")
    if event_type == "login":
        redis_client.lpush("global:events", f"User {username} logged in at {timestamp}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9000))
server.listen(5)
print("🔌 Serveur en écoute sur le port 9000...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
