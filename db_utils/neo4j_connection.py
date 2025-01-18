from neo4j import GraphDatabase

def get_protein_from_neo4j(protein_id):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

    with driver.session() as session:
        query = """
        MATCH (p:Protein {id: $protein_id})
        OPTIONAL MATCH (p)-[r]-(neighbor)
        RETURN p, collect(neighbor) AS neighbors
        """
        result = session.run(query, protein_id=protein_id)
        record = result.single()
        if record:
            return {"status": "success", "data": dict(record)}
        else:
            return {"status": "error", "message": "Protein not found"}
