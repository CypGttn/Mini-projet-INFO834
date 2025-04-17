import redis
import sys
import bcrypt

sys.stdout.reconfigure(encoding='utf-8')

# Connexion à Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r_services = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

def verify_user(username, password):
    user_key = f"user:{username}"
    user_data = r.hgetall(user_key)

    if not user_data:
        return False, "Utilisateur non trouvé."

    stored_password = user_data.get("password", "")

    try:
        # Vérifie si le mot de passe stocké est bien un hash bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return True, "User verified successfully."
        else:
            return False, "Mot de passe incorrect."
    except ValueError:
        return False, "Erreur de vérification du mot de passe."

def check_login_attempts(username):
    attempts_key = f"login_attempts:{username}"
    attempts = r.get(attempts_key)

    if attempts is None:
        r.setex(attempts_key, 600, 1)  # Expire après 10 minutes
        return True, "Connexion autorisée."

    attempts = int(attempts)

    if attempts >= 10:
        return False, "Trop de tentatives. Réessayez plus tard."

    r.incr(attempts_key)  # Incrémente les tentatives
    return True, "Connexion autorisée."

def log_login(username):
    """Ajoute l'utilisateur à la liste des 10 derniers connectés et met à jour le top des connexions."""
    r.lpush("last_logins", username)  
    r.ltrim("last_logins", 0, 9)  # Garde les 10 derniers

    r.zincrby("user_connections", 1, username)  # Incrémente les connexions de l'utilisateur

def log_user_connection(username):
    """Incrémente le nombre de connexions d'un utilisateur"""
    r.zincrby("user_connections", 1, username)

def get_top_3_users():
    return r.zrevrange("user_connections", 0, 2, withscores=True)

def get_last_10_logins():
    return r.lrange("last_logins", 0, 9)

if __name__ == "__main__":

    username = sys.argv[1]
    password = sys.argv[2]

    # Vérification de l'utilisateur
    user_valid, message = verify_user(username, password)
    if not user_valid:
        print(message)
        sys.exit(1)

    # Vérification du nombre de tentatives de connexion
    allowed, login_message = check_login_attempts(username)
    if not allowed:
        print(login_message)
        sys.exit(1)

    # Enregistrer la connexion
    log_login(username)
    print("Connexion réussie.")

    
