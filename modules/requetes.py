import re

class Requetes :
    def __init__(self, mongo_link, redis_link):
        self.mongo = mongo_link
        self.redis = redis_link
        
        # On récupère les utilisateurs de la base de données MongoDB
        self.db = self.mongo['lesBellesMiches']
        user = self.db['user']
        
        self.usernames = {user['username'] for user in user.find()}
    
    def total_users(self):
        # Nombre total d'utilisateurs connectés - Redis 
        count = 0
        connections = self.redis.lrange("global:events", 0, -1)
        for connection in connections : 
            if re.match(r"^User\s.+\slogged in\b", connection):
                count +=1
        return count
        
        
    def most_active_user(self):
        # Utilisateur qui se connecte le plus souvent - Redis
        
        # On récupère l'ensemble des users de la base de données       
        counts = {username : 0 for username in self.usernames}
        
        connections = self.redis.lrange("global:events", 0, -1)
        usernames = [connection.split(" ")[1] for connection in connections ]
        for user in usernames : 
            if user in counts.keys() : 
                counts[user] += 1
            else : 
                print(f"Nom d'utilisateur non trouvé dans la base de données : {user}")
        
        max = ""
        val_max = 0
        for user in self.usernames : 
            if counts[user] > val_max : 
                max = user
                val_max = counts[user]
        return max, val_max
        
    def most_messages_send(self):
        # Utilisateur qui envoit le plus de messages - MongoDB
        collection = self.db['message']
        counts = {username : 0 for username in self.usernames}
        
        for username in self.usernames:
            # On compte le nombre de messages envoyés par chaque utilisateur
            sent_messages = collection.find({"sender": username})
            for message in sent_messages:
                counts[username] += 1
        
        max = ""
        val_max = 0
        for user in self.usernames : 
            if counts[user] > val_max : 
                max = user
                val_max = counts[user]
        return max, val_max

         
    def most_messages_receive(self):
        # Utilisateur qui reçoit le plus de messages - MongoDB
        collection = self.db['message']
        counts = {username : 0 for username in self.usernames}
        
        for username in self.usernames:
            # On compte le nombre de messages envoyés par chaque utilisateur
            sent_messages = collection.find({"sender": username})
            for message in sent_messages:
                counts[username] += 1
        
        max = ""
        val_max = 0
        for user in self.usernames : 
            if counts[user] > val_max : 
                max = user
                val_max = counts[user]
        return max, val_max
        
