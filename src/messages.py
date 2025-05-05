'''
Classe permettant de :
    - voir l'ensemble des messages reçus 
    - envoyer un message
'''

import datetime


class Messages : 
    def __init__(self, dbMongo, username):
        self.db = dbMongo
        self.collection = self.db['message']
        self.username = username
        
    def received_messages_not_read(self):
        #Récupérer le ou les messages que l'user a reçu
        messages = self.collection.find({"recipient": self.username, "read": False})
        for message in messages:
            print(f"Sender {message['sender']}, Message : {message['text']}, Timestamp : {message['timestamp']}")
        self.collection.update_many({"recipient": self.username, "read": False}, {"$set": {"read": True}})
        return messages
    
    def received_messages_read(self):
        #Récupérer le ou les messages que l'user a reçu
        messages = self.collection.find({"recipient": self.username, "read": True})
        for message in messages:
            print(f"Sender {message['sender']}, Message : {message['text']}, Timestamp : {message['timestamp']}")
        return messages
    
    def send_message(self, recipient, message):
        # Envoyer un message à l'utilisateur mis en paramètre à partir de celui de connecté
        # Eléments nécessaire : sender, receipt, message, date
        sender = self.username
        recipient = recipient
        message = message
        timestamp = datetime.datetime.now()
        
        env = {"sender": sender, "recipient": recipient, "text": message, "timestamp": timestamp, "read": False}
        self.collection.insert_one(env)
        print('Message envoyé avec succès ! ')
    
    def sent_messages (self, username):
        #Récupérer le ou les messages que l'user a envoyé
        messages = self.collection.find({"sender": username})
        for message in messages:
            print(f"Receiver {message['recipient']}, Message : {message['text']}, Timestamp : {message['timestamp']}")
        