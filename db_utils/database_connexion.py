from neo4j import GraphDatabase
from pymongo import MongoClient

def connect_to_mongo_database():
    client = MongoClient('localhost', 27017)
    db = client['database']
    collection = db['proteins']
    return collection


def connect_to_neo4j_database():
    URI = "bolt://localhost:7687"
    AUTH = ("neo4j", "password")

    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    print("Connection established.")
    return driver

def close_neo4j_database(driver):
    driver.close()
    print("Connection closed.")