from SPARQLWrapper import SPARQLWrapper, JSON

# --- SPARQL Endpoint ---
sparql = SPARQLWrapper("http://localhost:8890/sparql")
sparql.setReturnFormat(JSON)

# --- SPARQL Query ---
query = """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX msc: <http://msc2010.org/resources/MSC/2010/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?prefix ?decade (COUNT(DISTINCT ?pub) AS ?count)
FROM <https://zbmath.org>
WHERE {
  ?pub a <https://schema.org/ScholarlyArticle> ;
       dct:issued ?year ;
       dct:subject ?msc .

  ?msc skos:notation ?notation .

  BIND(STR(?notation) AS ?mscCode)
  BIND(SUBSTR(?mscCode, 1, 2) AS ?prefix)

  FILTER(?prefix IN ("03", "60"))

  BIND(FLOOR(xsd:integer(STR(?year))/10)*10 AS ?decade)
}
GROUP BY ?prefix ?decade
ORDER BY ?prefix ?decade
"""

# --- Run Query ---
sparql.setQuery(query)
results = sparql.query().convert()

# --- Display Results ---
for row in results["results"]["bindings"]:
    prefix = row["prefix"]["value"]
    decade = row["decade"]["value"]
    count = row["count"]["value"]
    print(f"MSC {prefix} — {decade}s: {count} papers")
