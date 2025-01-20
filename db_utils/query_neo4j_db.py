from lib2to3.pgen2.tokenize import group

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
                r1.similarity AS similarity_1, 
                p2.ID AS p2,
                r2.similarity AS similarity_2,
                p3.ID AS p3
            """

        result = session.run(query, protein_id=protein_id).data()
    graph.close()
    return result


def isolated_nodes():
    graph = Neo4jGraph()
    with graph.driver.session() as session:
        query = """
            MATCH (p:Protein)
            WHERE NOT (p)-[]-()
            RETURN p.ID AS protein_id
            """
        result = session.run(query).data()
    graph.close()
    print(len(result))
    return result

