from pymongo import MongoClient

from pymongo import MongoClient

def get_protein_from_mongodb(field, value):
    # Connexion à MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["database"]
    collection = db["proteins"]

    try:
        # Recherche selon le champ
        if field == "Protein names":
            proteins = list(collection.find({"Protein names": {"$regex": value, "$options": "i"}}))
            for p in proteins:
                p["_id"] = str(p["_id"])  # Conversion de l'ID MongoDB en chaîne
            if proteins:
                return {"status": "success", "data": proteins}
            else:
                return {"status": "error", "message": "Aucune protéine trouvée pour le nom donné."}
        else:
            protein = collection.find_one({field: value})
            if protein:
                protein["_id"] = str(protein["_id"])  # Conversion de l'ID MongoDB en chaîne
                return {"status": "success", "data": protein}
            else:
                return {"status": "error", "message": "Aucune protéine trouvée pour la valeur donnée."}
    except Exception as e:
        # Gestion des erreurs
        return {"status": "error", "message": f"Une erreur s'est produite : {str(e)}"}
    finally:
        # Fermeture de la connexion
        client.close()
