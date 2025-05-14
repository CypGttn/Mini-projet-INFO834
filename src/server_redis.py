import redis
import sys
import bcrypt
from pymongo import MongoClient
import datetime

sys.stdout.reconfigure(encoding='utf-8')

# ───── Récupération du mot de passe Redis ───── #
redis_user = collection.find_one({"username": "cyp"})

if not redis_user or "password" not in redis_user:
    print("Mot de passe Redis introuvable dans MongoDB.")
    sys.exit(1)

redis_password = redis_user["password"]

# Ajoute ceci pour afficher le mot de passe récupéré
print(f"Mot de passe Redis récupéré depuis MongoDB : {redis_password}")

# ───── Connexion à Redis ───── #
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r_services = redis.Redis(host='localhost', port=6379, db=1, password=redis_password, decode_responses=True)

    # Test de connexion
    r.ping()
except redis.AuthenticationError:
    print("Mot de passe Redis incorrect.")
    sys.exit(1)
except Exception as e:
    print(f"Erreur de connexion à Redis : {e}")
    sys.exit(1)
    
def log_event(username, event_type):
    timestamp = datetime.datetime.now().isoformat()
    event_data = {
        "username": username,
        "timestamp": timestamp,
        "event": event_type
    }

    # Stockage dans une liste Redis (type list)
    r.lpush("user_events", str(event_data))
    
def get_user_logs():
    logs = r.lrange("user_events", 0, -1)
    for log in logs:
        print(log)


# ───── Fonctions d'authentification ───── #
def verify_user(username, password):
    user_key = f"user:{username}"
    user_data = r.hgetall(user_key)

    if not user_data:
        return False, "Utilisateur non trouvé."

    stored_password = user_data.get("password", "")

    try:
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return True, "Utilisateur vérifié avec succès."
        else:
            return False, "Mot de passe incorrect."
    except ValueError:
        return False, "Erreur de vérification du mot de passe."

def check_login_attempts(username):
    attempts_key = f"login_attempts:{username}"
    attempts = r.get(attempts_key)

    if attempts is None:
        r.setex(attempts_key, 600, 1)
        return True, "Connexion autorisée."

    attempts = int(attempts)

    if attempts >= 10:
        return False, "Trop de tentatives. Réessayez plus tard."

    r.incr(attempts_key)
    return True, "Connexion autorisée."

def log_login(username):
    r.lpush("last_logins", username)
    r.ltrim("last_logins", 0, 9)
    r.zincrby("user_connections", 1, username)

def log_user_connection(username):
    r.zincrby("user_connections", 1, username)

def get_top_3_users():
    return r.zrevrange("user_connections", 0, 2, withscores=True)

def get_last_10_logins():
    return r.lrange("last_logins", 0, 9)

# ───── Programme principal ───── #
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python script.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    user_valid, message = verify_user(username, password)
    if not user_valid:
        print(message)
        sys.exit(1)

    allowed, login_message = check_login_attempts(username)
    if not allowed:
        print(login_message)
        sys.exit(1)

    log_login(username)
    print("Connexion réussie.")
    
    log_event(username, "connexion")
    
    if len(sys.argv) == 4 and sys.argv[3] == "logout":
        log_event(username, "deconnexion")
        print("Déconnexion enregistrée.")
        sys.exit(0)
