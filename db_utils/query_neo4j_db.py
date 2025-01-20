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


def search_protein_by_id_with_double_neighbours(protein_id, limit=99999):
    graph = Neo4jGraph()
    with graph.driver.session() as session:
        query = """
        MATCH (p:Protein {ID: $protein_id})
        OPTIONAL MATCH (p)-[r1]-(n1)
        WITH p, r1, n1
          ORDER BY r1.similarity DESC
        WITH p, COLLECT(DISTINCT {neighbor: n1, relation: r1.similarity})[0..$limit] AS degree_1_neighbors
        UNWIND degree_1_neighbors AS d1
        WITH p, d1.neighbor AS n1, d1.relation AS r1_similarity, degree_1_neighbors
        OPTIONAL MATCH (n1)-[r2]-(n2)
        WHERE NOT n2 IN [n IN degree_1_neighbors | n.neighbor] // Exclusion des voisins de degré 1
        WITH p, degree_1_neighbors, n1, r2, n2
          ORDER BY r2.similarity DESC
        WITH p, degree_1_neighbors,
             COLLECT(DISTINCT {neighbor_1: n1, neighbor_2: n2, relation: r2.similarity})[0..$limit] AS degree_2_neighbors
        RETURN
          p AS protein,
          degree_1_neighbors,
          degree_2_neighbors
        """

        result = session.run(query, protein_id=protein_id, limit=limit).data()
    graph.close()

    result = result[0] if result else None


    ret = {}
    main_prot, degree_1_neighbors, degree_2_neighbors = result.values()

    ret['main_protein'] = {
        "ID": main_prot["ID"],
        "name": main_prot["name"],
        "sequence": main_prot["sequence"],
        "interpro": main_prot["interpro"]
    }

    ret['degree_1_neighbors'] = {}
    for neighbor in degree_1_neighbors:
        ret['degree_1_neighbors'][neighbor['neighbor']['ID']] = {
            "ID": neighbor['neighbor']['ID'],
            "name": neighbor['neighbor']['name'],
            "sequence": neighbor['neighbor']['sequence'],
            "interpro": neighbor['neighbor']['interpro'],
            "edge": {
                "from": main_prot['ID'],
                "similarity": neighbor['relation']
            }
        }

    ret['degree_2_neighbors'] = {}
    for neighbor in degree_2_neighbors:
        neighbor2_id = neighbor['neighbor_2']['ID']
        if neighbor2_id not in ret['degree_2_neighbors']:
            ret['degree_2_neighbors'][neighbor2_id] = {
                "ID": neighbor2_id,
                "name": neighbor['neighbor_2']['name'],
                "sequence": neighbor['neighbor_2']['sequence'],
                "interpro": neighbor['neighbor_2']['interpro'],
                "edge": [{
                    "from": neighbor['neighbor_1']['ID'],
                    "similarity": neighbor['relation']
                }]
            }
        else:
            ret['degree_2_neighbors'][neighbor2_id]['edge'].append({
                "from": neighbor['neighbor_1']['ID'],
                "similarity": neighbor['relation']
            })

    return ret


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

    res = search_protein_by_id_with_double_neighbours("A0A0B4J2F2")

    print(res)
