from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:3030/dataset/sparql")
sparql.setQuery("""
SELECT * WHERE { ?s ?p ?o } LIMIT 5
""")
sparql.setReturnFormat(JSON)

try:
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        print(result)
except Exception as e:
    print("Error:", e)
