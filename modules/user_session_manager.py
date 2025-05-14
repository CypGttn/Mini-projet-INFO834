import redis
import datetime
from pymongo import MongoClient
from bson import ObjectId
import bcrypt

class UserSessionManager:
    def __init__(
        self,
        mongo_uri='mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0',
        redis_host='localhost',
        redis_port=6379
    ):        
        # Initialisation de Redis
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)
        
        # Initialisation de MongoDB
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client['lesBellesMiches']
        self.users_collection = self.db['user']

    def log_event(self, user_id, event_type):
        timestamp = datetime.datetime.now().isoformat()
        event = f"{event_type}:{timestamp}"
        self.redis_client.lpush(f"user:{user_id}:events", event)

        if event_type == "login":
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                username = user.get("username")
                self.redis_client.lpush("global:events", f"User {username} logged in at {timestamp}")

        print(f"Utilisateur {user_id} {event_type} à {timestamp}")

    def afficher_utilisateurs(self):
        print("\nUtilisateurs présents dans la base :")
        for user in self.users_collection.find():
            print(f"- ID: {user.get('_id')} | username: {user.get('username')} | password: {user.get('password')}")

    def login_user(self, username, password):
        print(f"\nTentative de connexion pour : username='{username}'")
        self.afficher_utilisateurs()

        user = self.users_collection.find_one({"username": username})
        if user:
            print("Utilisateur trouvé.")
            stored_hash = user.get("password")

            try:
                # S'assurer que le mot de passe haché est bien des bytes
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')

                password_bytes = password.encode('utf-8')
                if bcrypt.checkpw(password_bytes, stored_hash):
                    user_id = str(user["_id"])
                    self.log_event(user_id, "login")
                    return user_id
                else:
                    print("Mot de passe incorrect.")
            except Exception as e:
                print(f"Erreur lors de la vérification du mot de passe : {e}")
        else:
            print("Utilisateur non trouvé.")

        return None

    def logout_user(self, user_id):
        self.log_event(user_id, "logout")

    def afficher_logs(self, user_id):
        logs = self.redis_client.lrange(f"user:{user_id}:events", 0, 9)
        if logs:
            print("\nDerniers logs de l'utilisateur :")
            for log in logs:
                print(log)
        else:
            print("Aucun log trouvé pour cet utilisateur.")

    def afficher_connexions_globales(self):
        global_logs = self.redis_client.lrange("global:events", 0, 9)
        if global_logs:
            print("\nDernières connexions globales :")
            for log in global_logs:
                print(log)
        else:
            print("Aucune connexion globale trouvée.")
