from pymongo import MongoClient

class db:
    def __init__(self, url, db_name):
        self.client = MongoClient(url)
        self.db = self.client[db_name]
    
    def insert(self, collection_name, data):
        self.db[collection_name].insert_one(data)

    def find(self, collection_name, query):
        return self.db[collection_name].find(query)

    def update(self, collection_name, query, data):
        self.db[collection_name].update_one(query, {'$set': data})

    def delete(self, collection_name, query):
        self.db[collection_name].delete_one(query)
        
    def close(self):
        self.client.close()