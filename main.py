from db_utils.database_creation import create_neo4j_database, create_mongo_database
from query_mongo_database import find_protein_by_id, compute_similarity_for_proteins, similarity_to_csv
from pathlib import Path




create_mongo_database()
proteins_similariy = compute_similarity_for_proteins()


graph = create_neo4j_database(proteins_similariy)
print(graph)