from database_connexion import connect_to_database

def find_protein_by_id(protein_id):
    # Connect to the database
    connection = connect_to_database()

    # Query the database
    result = connection.find_one({'Entry': protein_id})

    return result