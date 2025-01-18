from tqdm import tqdm

from db_utils.database_connexion import connect_to_mongo_database, connect_to_neo4j_database
from collections import Counter
from multiprocessing import Pool, cpu_count


def find_protein_by_id(protein_id):
    # Connect to the database
    connection = connect_to_mongo_database()

    # Query the database
    result = connection.find_one({'Entry': protein_id})

    return result



def hash_proteins_by_domain():
    # Connect to the database
    connection = connect_to_mongo_database()

    pipeline = [
        {"$unwind": "$InterPro"},
        {"$group": {
            "_id": "$InterPro",
            "proteins": {
                "$addToSet": {
                    "entry": "$Entry",
                    "interpro_count": "$InterPro_count"
                }
            },
        }},
        {"$project": {
            "InterPro_ID": "$_id",
            "proteins": 1,
            "_id": 0
        }}
    ]

    results = connection.aggregate(pipeline)
    interpro_dict = {result['InterPro_ID']: result['proteins'] for result in results}
    return interpro_dict


def jacard_similarity(ref_protein, domain_hash, min_threshold=0.):
    protein_id = ref_protein['Entry']
    # Find all proteins that share at least one domain with the protein of interest
    domains = set(ref_protein['InterPro'])
    proteins_to_compare = {}

    # Count the number of shared domains between the protein of interest and the other proteins
    for domain in domains:
        for protein2 in domains_hash[domain]:
            entry = protein2["entry"]
            if entry not in proteins_to_compare:
                proteins_to_compare[entry] = {"inter": 1, "InterPro_count": protein2["interpro_count"]}
            else:
                proteins_to_compare[entry]["inter"] += 1

    # Calculate the Jaccard similarity
    res_dict = {}
    for protein_entry, protein_infos in proteins_to_compare.items():
        interpro_count = protein_infos["InterPro_count"]
        inter = protein_infos["inter"]
        union = ref_protein["InterPro_count"] + interpro_count - inter
        res_dict[protein_entry] =  inter / union

    # Remove self (not present if no domain)
    if protein_id in res_dict:
        res_dict.pop(protein_id)

    # Remove proteins with a similarity below the threshold
    res_dict = {k: v for k, v in res_dict.items() if v >= min_threshold}

    # Sort by similarity
    res_dict = dict(sorted(res_dict.items(), key=lambda item: item[1], reverse=True))

    return res_dict



if __name__ == '__main__':
    connection = connect_to_mongo_database()

    proteins = connection.aggregate([{"$sample": {"size": 20000}}, {"$project": {"Entry": 1, "InterPro": 1, "InterPro_count": 1, "_id": 0}}])
    proteins = list(proteins)

    # Hash proteins by domain for faster comparison
    domains_hash = hash_proteins_by_domain()

    res = {}
    for protein in tqdm(proteins):
        res[protein["Entry"]] = jacard_similarity(protein, domains_hash, min_threshold=0.5)

    print(res)