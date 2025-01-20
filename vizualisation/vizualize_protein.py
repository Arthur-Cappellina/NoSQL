from d3blocks import D3Blocks
import networkx as nx
from numpy import Inf

from db_utils.query_neo4j_db import search_protein_by_id


def create_graph(data, nodes_limit=Inf, show_neighbours_edges=True):
    # Construire le graphe
    G = nx.Graph()

    # Ajouter les nœuds et les arêtes
    G.add_node(data[0]["p1"])

    done = set()
    i = 0
    for d in data:
        p2 = d["p2"]
        G.add_node(p2)
        G.add_edge(d["p1"], p2, similarity=d["similarity_1"])

        if p2 not in done:
            done.add(p2)
            i += 1
        if i >= nodes_limit:
            break

    if show_neighbours_edges:
        for d in data:
            if d["p2"] in done and d["p3"] in done:
                G.add_node(d["p3"])
                G.add_edge(d["p2"], d["p3"], similarity=d["similarity_2"])



    return G





def display_protein_neighbours(graph, main_protein):

    # Convert the graph to a pandas dataframe
    df = nx.to_pandas_edgelist(graph)
    df['weight'] = df['source'].apply(lambda x: 2 if x == main_protein else 1)

    # Initialize D3Blocks
    d3 = D3Blocks()

    # Create the network graph
    d3.d3graph(df, filepath='d3graph.html', scaler='minmax', collision=1, charge=5000, showfig=False)

    # Customize node properties
    # For other proteins nodes
    d3.D3graph.set_node_properties(size=10, color="#ADD8E6", fontcolor="#000000", fontsize=15)  # Default color and size

    # For main protein node
    d3.D3graph.node_properties[main_protein]['size'] = 30  # Highlight the main protein
    d3.D3graph.node_properties[main_protein]['fontsize'] = 20
    d3.D3graph.node_properties[main_protein]['color'] = '#FF0000'  # Red for the main protein
    d3.D3graph.node_properties[main_protein]['edge_color'] = '#000000'
    d3.D3graph.node_properties[main_protein]['edge_size'] = 1


    # Customize edge properties
    d3.D3graph.set_edge_properties(directed=False, label_color='#000000')  # Default color and size
    for idx, row in df.iterrows():
        # Add weight as edge label
        if row['source'] == main_protein:
            d3.D3graph.edge_properties[(row['source'], row['target'])]['color'] = '#FF0000'
            d3.D3graph.edge_properties[(row['source'], row['target'])]['edge_weight'] = 1
        else:
            d3.D3graph.edge_properties[(row['source'], row['target'])]['color'] = '#000000'
        d3.D3graph.edge_properties[(row['source'], row['target'])]['label'] = round(row['similarity'], 2)

    # Show the graph
    d3.D3graph.show(show_slider=False, save_button=False)



def display_protein(data, main_protein, nodes_limit=20, show_neighbours_edges=True):
    g = create_graph(data, nodes_limit=nodes_limit, show_neighbours_edges=show_neighbours_edges)
    display_protein_neighbours(g, main_protein)


if __name__ == "__main__":
    MAIN_PROTEIN = "A0A0B4J2F2"
    data = search_protein_by_id(MAIN_PROTEIN)
    display_protein(data, MAIN_PROTEIN, nodes_limit=20, show_neighbours_edges=False)
