import csv
from db_utils.database_connection import connect_to_mongo_database
from db_utils.database_connection import Neo4jGraph
from db_utils.query_mongo_database import compute_similarity_for_proteins


def create_mongo_database():
    # Connect to the database
    collection = connect_to_mongo_database()

    # Drop the collection if it already exists
    collection.drop()

    file_path = 'data/data_small.tsv'

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


def create_neo4j_database(proteins_dict_similarity):
    graph = Neo4jGraph()
    graph.reset_graph()

    # Create nodes and edges
    nodes = []
    edges = []

    for protein_id, values in proteins_dict_similarity.items():
        # node
        nodes.append({
            "protein_id":  protein_id,
            "type": "Protein",
            "name": values["name"],
            "sequence": values["sequence"],
            "interpro": values["interpro"]
        })

        # edges
        for protein_id2, similarity_score in values["similarities"].items():
            edges.append({
                "protein_id_1": protein_id,
                "protein_id_2": protein_id2 ,
                "similarity": similarity_score
            })

    graph.create_graph(nodes, edges)
    return graph


if __name__ == "__main__":
    create_mongo_database()
    proteins_similarity = compute_similarity_for_proteins()
    graph = create_neo4j_database(proteins_similarity)
    print("Database creation done.")