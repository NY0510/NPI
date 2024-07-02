from pymongo import MongoClient

class db:
    def __init__(self, url, db_name):
        self.client = MongoClient(url)
        self.db = self.client[db_name]
    
    def insert(self, collection_name, data):
        self.db[collection_name].insert_one(data)

    def find(self, collection_name, query, projection=None):
        return self.db[collection_name].find(query, projection)

    def find_one(self, collection_name, query, projection=None):
        return self.db[collection_name].find_one(query, projection)
    
    def update(self, collection_name, query, data):
        self.db[collection_name].update_one(query, {'$set': data})
    
    def update_one(self, collection_name, query, data):
        self.db[collection_name].update_one(query, data)

    def delete(self, collection_name, query):
        self.db[collection_name].delete_one(query)
        
    def delete_many(self, collection_name, query):
        self.db[collection_name].delete_many(query)
        
    def close(self):
        self.client.close()