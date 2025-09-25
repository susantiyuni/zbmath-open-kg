from SPARQLWrapper import SPARQLWrapper, JSON

# --- CONFIGURATION ---
endpoint_url = "http://localhost:8890/sparql"  # Virtuoso SPARQL endpoint

sparql = SPARQLWrapper(endpoint_url)
sparql.setReturnFormat(JSON)

# --- STEP 1: Sample early papers with MSC + keyword filter ---
# Construct the SPARQL query
reviewed_query = f"""
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?paper ?title ?year ?authorName
FROM <https://zbmath.org>
WHERE {{
  ?paper a schema:ScholarlyArticle ;
         schema:review ?rev ;
         dcterms:title ?title ;
         schema:datePublished ?year ;
         dcterms:creator ?author .
  ?rev schema:author ?reviewer .
  ?reviewer schema:name "Serre, Jean-Pierre" .
  ?author schema:name ?authorName
}}
ORDER BY ?year
ORDER BY RAND()
LIMIT 100
"""

sparql.setQuery(reviewed_query)
early_results = sparql.query().convert()
early_ids = [res["early"]["value"] for res in early_results["results"]["bindings"]]
print (early_ids)
# import sys
# sys.exit()

# --- STEP 2: Sample later papers with MSC + keyword filter ---
authored_query = f"""
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?paper ?title ?year ?msc
WHERE {{
  ?paper a schema:ScholarlyArticle ;
         schema:author ?serre ;
         dcterms:title ?title ;
         schema:datePublished ?year ;
         dcterms:subject ?msc .
  ?serre schema:name "Serre, Jean-Pierre" .
}}
ORDER BY ?year
ORDER BY RAND()
LIMIT 100
"""
sparql.setQuery(authored_query)
later_results = sparql.query().convert()
later_ids = [res["later"]["value"] for res in later_results["results"]["bindings"]]
print (later_ids)
# import sys
# sys.exit()

# --- STEP 3: Join early/later papers on shared MSC and keywords ---
early_values = " ".join(f"<{eid}>" for eid in early_ids)
later_values = " ".join(f"<{lid}>" for lid in later_ids)

join_query = f"""
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

LIMIT 100
"""
sparql.setQuery(join_query)
join_results = sparql.query().convert()

# --- Print the results ---
for row in join_results["results"]["bindings"]:
    print(f"{row['earlyTitle']['value']} ({row['earlyYear']['value']}) [{row['earlyMSC']['value']}] --> "
          f"{row['laterTitle']['value']} ({row['laterYear']['value']}) [{row['laterMSC']['value']}]")
    print("Shared keywords:", row.get("sharedKeywords", {}).get("value", ""))
    print("---")
