from pymongo import MongoClient

def connect_to_database():
    client = MongoClient('localhost', 27017)
    db = client['database']
    collection = db['proteins']
    return collection
