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
        
    def received_messages(self):
        #Récupérer le ou les messages que l'user a reçu
        messages = self.collection.find({"recipient": self.username})
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