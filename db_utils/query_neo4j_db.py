from db_utils.database_connection import Neo4jGraph


def search_protein_by_id(protein_id):
    graph = Neo4jGraph()
    with graph.driver.session() as session:
        query =  """
            MATCH (p:Protein {ID: $protein_id})-[r1]-(p2:Protein)
            OPTIONAL MATCH (p2)-[r2]-(p3:Protein)
            WHERE EXISTS { 
                MATCH (p)-[]-(p3)
            }
            RETURN 
                p.ID AS p1, 
                p.sequence AS sequence1,
                p.interpro AS interpro1, 
                r1.similarity AS similarity_1,
                p2.ID AS p2,
                p2.sequence AS sequence2,
                p2.interpro AS interpro2,
                r2.similarity AS similarity_2,
                p3.ID AS p3
            """

        result = session.run(query, protein_id=protein_id).data()
    graph.close()
    return result


def search_protein_by_id_with_double_neighbours(protein_id, limit=10):
    graph = Neo4jGraph()
    with graph.driver.session() as session:
        query = """
                MATCH (p:Protein {ID: $protein_id})
                OPTIONAL MATCH (p)-[r1]-(n1)
                WITH p, r1, n1
                ORDER BY n1 IS NULL, r1.similarity DESC
                LIMIT $limit
                OPTIONAL MATCH (n1)-[r2]-(n2)
                WITH p, r1, n1, r2, n2
                ORDER BY n2 IS NULL, r2.similarity DESC
                LIMIT $limit
                RETURN
                  p AS protein,
                  COLLECT({neighbor: n1, relation: r1}) AS degree_1_neighbors,
                  COLLECT({neighbor: n2, relation: r2}) AS degree_2_neighbors
                """

        result = session.run(query, protein_id=protein_id, limit=limit).data()
    graph.close()

    return result


def isolated_proteins():
    graph = Neo4jGraph()
    with graph.driver.session() as session:
        query = """
            MATCH (p:Protein)
            WHERE NOT (p)-[]-()
            RETURN p.ID AS protein_id
            """
        result = session.run(query).data()
    graph.close()
    return result


def compute_stats_neo4j():
    return {
        "isolated_proteins": len(isolated_proteins())
    }


if __name__ == "__main__":

    res = search_protein_by_id_with_double_neighbours("A0A0B4J2F2")[0]
    for key, value in res.items():
        print("------------------------------------\n" + key)
        for key2, value2 in value.items():
            print(key2, value2)
        print("\n")
