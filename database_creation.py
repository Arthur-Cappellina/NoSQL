import csv
from pymongo import MongoClient
from database_connexion import connect_to_database

# Connect to the database
collection = connect_to_database()

# Open tsv file and create a database with the data mongoDB
with open('data_small.tsv', 'r') as tsvfile:
    reader = csv.reader(tsvfile, delimiter='\t')
    headers = next(reader)  # Read the header row
    
    for row in reader:
        # Convert the row to a dictionary using the headers
        document = dict(zip(headers, row))

        # Insert data into the database
        collection.insert_one(document)
