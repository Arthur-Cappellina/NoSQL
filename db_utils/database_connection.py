from neo4j import GraphDatabase
from pymongo import MongoClient
from tqdm import tqdm


def connect_to_mongo_database():
    client = MongoClient('localhost', 27017)
    db = client['database']
    collection = db['proteins']
    return collection


class Neo4jGraph:
    def __init__(self):
        URI = "bolt://localhost:7687"
        AUTH = ("neo4j", "password")
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.driver.verify_connectivity()
        print("Connection to neo4j established.")

    def reset_graph(self):
        with self.driver.session() as session:
            print("Resetting graph...")

            # Delete all nodes and relationships
            session.run("MATCH (n) DETACH DELETE n")

            # Delete all constraints
            constraints = session.run("SHOW CONSTRAINTS").data()
            for constraint in constraints:
                name = constraint['name']
                session.run(f"DROP CONSTRAINT {name}")

            # Delete all indexes
            indexes = session.run("SHOW INDEXES").data()
            for index in indexes:
                name = index['name']
                session.run(f"DROP INDEX {name}")

        print("Graph reset.")


    def close(self):
        self.driver.close()
        print("Connection closed.")


    def create_graph(self, nodes, edges):
        with self.driver.session() as session:

            self.create_constraint()

            session.execute_write(self._load_nodes, nodes)
            session.execute_write(self._load_edges, edges)

        self.close()


    def create_constraint(self):
        # Allow to accelerate the search for a node by indexing the `Protein.ID` property
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT FOR (p:Protein) REQUIRE p.ID IS UNIQUE")
        print("Constraint on `Protein.ID` created.")


    @staticmethod
    def _load_nodes(tx, nodes, batch_size=1000):
        for i in tqdm(range(0, len(nodes), batch_size), desc="Loading nodes"):
            batch = nodes[i:i + batch_size]
            query = "UNWIND $batch AS row CREATE (n:Protein) SET n.ID = row['protein_id'], n.type = row['type']"
            tx.run(query, batch=batch)

        print("Nodes successfully loaded.")


    @staticmethod
    def _load_edges(tx, edges, batch_size=10000):
        for i in tqdm(range(0, len(edges), batch_size), desc="Loading edges"):
            batch = edges[i:i + batch_size]
            query = """
            UNWIND $batch AS row
            MATCH (a:Protein {ID: row.protein_id_1}), (b:Protein {ID: row.protein_id_2})
            MERGE (a)-[r:SIMILAR_TO]-(b)
            ON CREATE SET r.similarity = row.similarity
            """
            tx.run(query, batch=batch)

        print("Edges successfully loaded.")


    def search_protein_by_id(self, protein_id):
        with self.driver.session() as session:
            result = session.run("MATCH (p:Protein {ID: $protein_id}) RETURN p", protein_id=protein_id).data()
        return result
