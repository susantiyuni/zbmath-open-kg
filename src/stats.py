from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:8890/sparql")

def run_query(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()["results"]["bindings"]

print (f"✅ Triple Samples: ")

# 0. Sample triples
sample_q = """
SELECT * FROM <https://zbmath.org> WHERE { ?s ?p ?o } LIMIT 5
# SELECT COUNT(*) WHERE { GRAPH <https://zbmath.org> { ?s ?p ?o } };
"""
sample_triples = run_query(sample_q)
for r in sample_triples:
    print (r)

print (f"✅ Metrics: ")

# 1. Entities
entities_q = """
SELECT (COUNT(*) AS ?count)
FROM <https://zbmath.org>
WHERE {
  {
    SELECT DISTINCT ?entity
    FROM <https://zbmath.org>
    WHERE { 
      { ?entity ?p ?o } 
      UNION 
      { ?s ?p ?entity } 
    }
  }
}

"""
entities = int(run_query(entities_q)[0]["count"]["value"])
print("Entities:", entities)

# 2. Edges
edges_q = """
SELECT (COUNT(*) AS ?count)
FROM <https://zbmath.org>
WHERE { ?s ?p ?o }
"""
# edges = int(run_query(edges_q)[0]["count"]["value"])
edges = 159154246
print("Edges/Triples:", edges)

# 3. Average Degree
avg_degree = 2 * edges / entities
print("Average Degree:", round(avg_degree, 2))

# 4. Density
density = edges / (entities * (entities - 1))
print("Graph Density:", "{:.2e}".format(density))

# 5. Relation Types
preds_q = """
SELECT (COUNT(DISTINCT ?p) AS ?count)
FROM <https://zbmath.org>
WHERE { ?s ?p ?o }
"""
relations = int(run_query(preds_q)[0]["count"]["value"])
print("Relation Types:", relations)

# 6. Entity Types
ent_type_q = """
SELECT ?type (COUNT(DISTINCT ?entity) AS ?count)
FROM <https://zbmath.org>
WHERE {
  ?entity a ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
"""
ent_types = run_query(ent_type_q)
for type in ent_types:
    print (type)

# 7. Entity Types (rdf:type and dcterms:type coverage)
typed_ent_q = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT
  (COUNT(DISTINCT ?typedEntity) AS ?typedCount)
  (COUNT(DISTINCT ?entity) AS ?totalCount)
  ((COUNT(DISTINCT ?typedEntity) * 100.0) / COUNT(DISTINCT ?entity) AS ?typeCoveragePercent)
FROM <https://zbmath.org>
WHERE {
  {
    SELECT DISTINCT ?entity
    WHERE {
      { ?entity ?p ?o } UNION { ?s ?p ?entity }
    }
  }
  OPTIONAL {
    {
      ?entity rdf:type ?anyType .
    }
    UNION
    {
      ?entity dcterms:type ?anyType .
    }
    BIND(?entity AS ?typedEntity)
  }
}
"""
typed_ent = run_query(typed_ent_q)
typed_count = typed_ent[0]["typedCount"]["value"]
total_count = typed_ent[0]["totalCount"]["value"]
type_coverage = typed_ent[0]["typeCoveragePercent"]["value"]
print(f"Entities with rdf:type or dcterms:type: {typed_count}/{total_count} ({type_coverage}%)")

# 8. Distinct Authors and Reviewers
author_reviewer_q = """
PREFIX schema: <https://schema.org/>

SELECT
  (COUNT(DISTINCT ?author) AS ?totalDistinctAuthors)
  (COUNT(DISTINCT ?reviewer) AS ?totalDistinctReviewers)
FROM <https://zbmath.org>
WHERE {
  OPTIONAL { ?article schema:author ?author . }
  OPTIONAL { ?article schema:review/schema:reviewer ?reviewer . }
}
"""

author_reviewer = run_query(author_reviewer_q)
authors = author_reviewer[0]["totalDistinctAuthors"]["value"]
reviewers = author_reviewer[0]["totalDistinctReviewers"]["value"]

print(f"Distinct Authors: {authors}")
print(f"Distinct Reviewers: {reviewers}")
