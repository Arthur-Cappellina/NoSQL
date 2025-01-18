import csv
from NoSQL.db_utils.database_connection import connect_to_mongo_database
from NoSQL.db_utils.database_connection import connect_to_neo4j_database


def create_mongo_database():
    # Connect to the database
    collection = connect_to_mongo_database()

    # Drop the collection if it already exists
    collection.drop()

    file_path = '../data/data_small.tsv'

    # Open tsv file and create a database with the data mongoDB
    with open(file_path, 'r') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        batch_size = 1000
        buffer = []

        headers = next(reader)

        for row in reader:
            document = {headers[i]: row[i] for i in range(len(headers))}

            # Convert the 'InterPro' field into a list
            if 'InterPro' in document:
                document['InterPro'] = document['InterPro'].split(';')[:-1] if document['InterPro'] else []
                document["InterPro_count"] = len(document['InterPro']) if document['InterPro'] else 0

            # Insert data into the database when the buffer is full to speed up the process
            buffer.append(document)
            if len(buffer) >= batch_size:
                collection.insert_many(buffer)
                buffer = []

        if len(buffer) > 0:
            collection.insert_many(buffer)

        collection.create_index([('InterPro', 1)])

        print("Data successfully inserted into the database.")


def create_neo4j_database(proteins):
    driver = connect_to_neo4j_database()
    pass


def insert_proteins_into_neo4j(adjacence_matrix):
    driver = connect_to_neo4j_database()
    with driver.session() as session:
        pass



create_mongo_database()