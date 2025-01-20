from flask import Flask, render_template, request, jsonify, make_response
from db_utils.query_mongo_db import get_protein_from_mongodb, compute_stats_mongodb
from db_utils.query_neo4j_db import compute_stats_neo4j, search_protein_by_id_with_double_neighbours
from db_utils.query_neo4j_db import search_protein_by_id
from vizualisation.vizualize_protein import display_protein

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/graph", methods=["GET"])
def graph():
    return render_template("graph.html", protein_id="", nodes_limit=10, show_neighbours_edges="true")

@app.route("/visualize_graph", methods=["GET"])
def visualize_graph():
    # Récupérer les paramètres
    protein_id = request.args.get("protein_id")
    nodes_limit = int(request.args.get("nodes_limit", "infinity"))
    show_neighbours_edges_val = request.args.get("show_neighbours_edges", "true")
    show_neighbours_edges = show_neighbours_edges_val.lower() in ["oui", "true"]

    # Vérification des paramètres
    if not protein_id:
        return jsonify({"status": "error", "message": "Protein ID is required"}), 400

    try:
        data = search_protein_by_id(protein_id)
        html_content = display_protein(data, protein_id, nodes_limit=nodes_limit, show_neighbours_edges=show_neighbours_edges)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    # Injecter le formulaire et la barre de navigation en haut de la page
    top_bar_and_form = render_template("partial/top_bar_and_form.html", protein_id=protein_id, nodes_limit=nodes_limit, show_neighbours_edges=show_neighbours_edges_val)
    if "<body>" in html_content:
        html_content = html_content.replace("<body>", f"<body>{top_bar_and_form}")

    # Retourner directement le HTML généré
    return html_content, 200, {'Content-Type': 'text/html'}


@app.route("/stats", methods=["GET"])
def stats():
    return render_template("stats.html")

@app.route("/compute_stats", methods=["GET"])
def compute_stats_route():
    results_mongo = compute_stats_mongodb()
    results_neo4j = compute_stats_neo4j()
    json_results = {**results_mongo, **results_neo4j}

    return jsonify(json_results)

@app.route("/query_db", methods=["GET"])
def query_mongodb():
    search_type = request.args.get("type")  # Type de recherche (id, name, description)
    search_value = request.args.get("value")  # Valeur entrée par l'utilisateur
    db_type = request.args.get("db").lower()  # Type de base de données (mongodb, neo4j)


    if db_type == "mongodb":
        # Mapping du type de recherche à la clé MongoDB
        search_field_map = {
            "id": "Entry",
            "name": "Entry Name",
            "description": "Protein names",
            "id-name": ["Entry", "Entry Name"],
            "id-description": ["Entry", "Protein names"],
            "name-description": ["Entry Name", "Protein names"],
            "id-name-description": ["Entry", "Entry Name", "Protein names"]
        }

        # Validation du type de recherche
        search_field = search_field_map.get(search_type)
        if not search_field:
            return jsonify({"status": "error", "message": "Type de recherche invalide"}), 400

        # Requête MongoDB
        result = get_protein_from_mongodb(search_field, search_value)

    elif db_type == "neo4j":
        result = search_protein_by_id_with_double_neighbours(search_value)
        return jsonify(result)

    else:
        return jsonify({"status": "error", "message": "Type de base de données invalide"}), 400


    return jsonify(result)

@app.route("/query_neo4j", methods=["GET"])
def query_neo4j():
    protein_id = request.args.get("protein_id")
    result = search_protein_by_id(protein_id)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
