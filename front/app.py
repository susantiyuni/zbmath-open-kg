from flask import Flask, request, jsonify, send_from_directory
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__, static_folder="static")

# SPARQL_ENDPOINT = "http://localhost:7200/repositories/zbmath-kg" #graphdb
SPARQL_ENDPOINT = "http://localhost:3030/dataset/sparql" #fuseki

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    sparql_query = data.get("query")
    if not sparql_query:
        return jsonify({"error": "No query provided"}), 400

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
