import redis
import datetime
from pymongo import MongoClient
from bson import ObjectId  # Ajouter cette ligne pour importer ObjectId

# Connexion à Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Connexion à MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['lesBellesMiches']
users_collection = db['user']

def log_event(user_id, event_type):
    timestamp = datetime.datetime.now().isoformat()
    event = f"{event_type}:{timestamp}"

    # Ajouter l'événement à la liste des logs de l'utilisateur spécifique
    redis_client.lpush(f"user:{user_id}:events", event)
    
    # Ajouter l'événement de connexion globalement avec le username
    if event_type == "login":  # On ne loggue que les connexions globales
        # Trouver le username de l'utilisateur à partir de l'ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})  # Utiliser ObjectId pour la conversion
        if user:
            username = user.get("username")
            # Ajouter l'événement de connexion global avec le username
            redis_client.lpush("global:events", f"User {username} logged in at {timestamp}")
    
    print(f"Utilisateur {user_id} {event_type} à {timestamp}")

def afficher_utilisateurs():
    print("\nUtilisateurs présents dans la base :")
    for user in users_collection.find():
        print(f"- ID: {user.get('_id')} | username: {user.get('username')} | password: {user.get('password')}")

def login_user(username, password):
    print(f"\nTentative de connexion pour : username='{username}'")

    afficher_utilisateurs()

    user = users_collection.find_one({"username": username})

    if user:
        print("Utilisateur trouvé.")
        if user.get("password") == password:
            user_id = str(user["_id"])
            log_event(user_id, "login")
            return user_id
        else:
            print("Mot de passe incorrect.")
    else:
        print("Utilisateur non trouvé.")

    return None

def logout_user(user_id):
    log_event(user_id, "logout")

def afficher_logs(user_id):
    # Récupérer les 10 derniers logs de l'utilisateur
    logs = redis_client.lrange(f"user:{user_id}:events", 0, 9)  # Récupère les 10 derniers logs
    if logs:
        print("\nDerniers logs de l'utilisateur :")
        for log in logs:
            print(log)
    else:
        print("Aucun log trouvé pour cet utilisateur.")

def afficher_connexions_globales():
    # Récupérer les 10 dernières connexions globales
    global_logs = redis_client.lrange("global:events", 0, 9)
    if global_logs:
        print("\nDernières connexions globales :")
        for log in global_logs:
            print(log)
    else:
        print("Aucune connexion globale trouvée.")

# Exécution principale
user_id = login_user("alice", "alice")
if user_id:
    input("Connecté. Appuyez sur Entrée pour se déconnecter...")
    logout_user(user_id)
    afficher_logs(user_id)  # Afficher les derniers logs de l'utilisateur
    afficher_connexions_globales()  # Afficher les dernières connexions globales
else:
    print("Échec de la connexion.")
