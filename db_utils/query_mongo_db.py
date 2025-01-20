from pymongo import MongoClient
from db_utils.database_connection import connect_to_mongo_database


def is_array(value):
    return isinstance(value, list)


def get_protein_from_mongodb(field, value):
    collection = connect_to_mongo_database()

    try:
        # Recherche selon le champ
        if is_array(field):
            results = []
            for f in field:
                res = get_protein_from_mongodb(f, value)
                if res["status"] == "success":
                    results.append(res["data"])
            if len(results) == 0:
                return "Aucune protéine trouvée pour les valeurs données."
            return {"status": "success", "data": results}
        elif field == "Protein names":
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


def compute_stats_mongodb():
    collection = connect_to_mongo_database()

    total_proteins = collection.count_documents({})

    return {
        "total_proteins": total_proteins,
        "unlabelled_proteins": collection.count_documents({"$or": [{"EC number": {"$exists": False}}, {"EC number": ""}]}),
        "labelled_proteins": collection.count_documents({"EC number": {"$exists": True, "$ne": ""}}),
    }