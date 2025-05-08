'''
Classe permettant de :
    - voir l'ensemble des messages reçus 
    - envoyer un message
'''

import datetime


class Messages : 
    def __init__(self, dbMongo, user_id):
        self.db = dbMongo
        self.collection_messages = self.db['message']
        self.collection_users = self.db['user']
        self.user_id = user_id
        
    def received_messages_not_read(self):
        if not self.collection.find_one({"recipient": self.user_id, "read": False}):
            print("Aucun message reçu non lu.")
        else : 
            #Récupérer le ou les messages que l'user a reçu
            messages = self.collection.find({"recipient": self.user_id, "read": False})
            for message in messages:
                print(f"Sender {message['sender']}, Message : {message['text']}, Timestamp : {message['timestamp']}")
            self.collection.update_many({"recipient": self.user_id, "read": False}, {"$set": {"read": True}})
            return messages
    
    def received_messages_read(self):
        if not self.collection.find_one({"recipient": self.user_id, "read": True}):
            print("Aucun message reçu.")
        else : 
            #Récupérer le ou les messages que l'user a reçu
            messages = self.collection.find({"recipient": self.user_id, "read": True})
            for message in messages:
                print(f"Sender {message['sender']}, Message : {message['text']}, Timestamp : {message['timestamp']}")
            return messages
        
    def send_message(self, recipient_id, message):
        # Envoyer un message à l'utilisateur mis en paramètre à partir de celui de connecté
        # Eléments nécessaire : sender, receipt, message, date
        sender_id = self.user_id
        message = message
        timestamp = datetime.datetime.now()
        
        env = {"sender": sender_id, "recipient": recipient_id, "text": message, "timestamp": timestamp, "read": False}
        self.collection.insert_one(env)
        print('Message envoyé avec succès ! ')
    
    def sent_messages (self, user_id):
        if not self.collection.find_one({"sender": user_id}):
            print("Aucun message envoyés.")
        else : 
            #Récupérer le ou les messages que l'user a reçu
            messages = self.collection.find({"sender": user_id})
            for message in messages:
                print(f"recipient {message['recipient']}, Message : {message['text']}, Timestamp : {message['timestamp']}")
        