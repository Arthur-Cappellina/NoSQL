from tqdm import tqdm
from db_utils.database_connection import connect_to_mongo_database



def find_protein_by_id(protein_id):
    # Connect to the database
    connection = connect_to_mongo_database()

    # Query the database
    result = connection.find_one({'Entry': protein_id})

    return result



def hash_proteins_by_domain(proteins=None):
    # Connect to the database
    connection = connect_to_mongo_database()

    pipeline = []

    if proteins:
        pipeline.append({"$match": {"Entry": {"$in": proteins}}})

    pipeline.extend([
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
    ])

    results = connection.aggregate(pipeline)
    interpro_dict = {result['InterPro_ID']: result['proteins'] for result in results}
    return interpro_dict


def jacard_similarity(ref_protein, domains_hash, min_threshold=0.):
    protein_id = ref_protein['Entry']
    # Find all proteins that share at least one domain with the protein of interest
    domains = set(ref_protein['InterPro'])
    proteins_to_compare = {}

    # Count the number of shared domains between the protein of interest and the other proteins
    for domain in domains:

        # Remove the protein of interest from the list of proteins sharing the domain
        domains_hash[domain] = [
            protein1 for protein1 in domains_hash[domain] if protein1["entry"] != protein_id
        ]

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



def compute_similarity_for_proteins(proteins=None):
    if proteins is None:
        connection = connect_to_mongo_database()
        proteins = connection.aggregate([{"$project": {"Entry": 1, "InterPro": 1, "InterPro_count": 1, "_id": 0}}])
        proteins = list(proteins)

    # Hash proteins by domain for faster comparison
    domains_hash = hash_proteins_by_domain(proteins=[protein["Entry"] for protein in proteins])

    res = {}
    for protein in tqdm(proteins):
        res[protein["Entry"]] = jacard_similarity(protein, domains_hash, min_threshold=0.5)

    return res



def similarity_to_csv(similarity_dict, node_file, relationship_file):
    with open(node_file, 'w') as node_file, open(relationship_file, 'w') as relationship_file:
        node_file.write("Id,Label\n")
        relationship_file.write("Source,Target,Weight\n")

        for protein, similarities in similarity_dict.items():
            node_file.write(f"{protein},Protein\n")
            for similar_protein, similarity in similarities.items():
                relationship_file.write(f"{protein},{similar_protein},{similarity}\n")
    print("CSV files successfully created.")
