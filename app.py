from flask import Flask, render_template, request, jsonify
from db_utils.mongodb_connection import get_protein_from_mongodb
from db_utils.neo4j_connection import get_protein_from_neo4j

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query_mongodb", methods=["GET"])
def query_mongodb():
    search_type = request.args.get("type")  # Type de recherche (id, name, description)
    search_value = request.args.get("value")  # Valeur entrée par l'utilisateur

    # Mapping du type de recherche à la clé MongoDB
    search_field_map = {
        "id": "Entry",
        "name": "Entry Name",
        "description": "Protein names"
    }

    # Validation du type de recherche
    search_field = search_field_map.get(search_type)
    if not search_field:
        return jsonify({"status": "error", "message": "Type de recherche invalide"}), 400

    # Requête MongoDB
    result = get_protein_from_mongodb(search_field, search_value)
    return jsonify(result)

@app.route("/query_neo4j", methods=["GET"])
def query_neo4j():
    protein_id = request.args.get("protein_id")
    result = get_protein_from_neo4j(protein_id)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
