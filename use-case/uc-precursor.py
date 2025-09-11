from SPARQLWrapper import SPARQLWrapper, JSON

# --- CONFIGURATION ---
endpoint_url = "http://localhost:8890/sparql"  # Virtuoso SPARQL endpoint
keywords = [
    "https://zbmath.org/keyword/MValgebra",
    "https://zbmath.org/keyword/BCIalgebra",
    "https://zbmath.org/keyword/BCKalgebra",
    "https://zbmath.org/keyword/fuzzy_ideal"
]

msc_codes = ["03", "06"]

keywords_values = "\n    ".join(f"<{k}>" for k in keywords)
msc_filters = " ||\n    ".join(
    f'STRSTARTS(STR(?msc), "http://msc2010.org/resources/MSC/2010/{code}")' 
    for code in msc_codes
)

sparql = SPARQLWrapper(endpoint_url)
sparql.setReturnFormat(JSON)

# --- STEP 1: Sample early papers with MSC + keyword filter ---
# Construct the SPARQL query
early_query = f"""
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>
PREFIX msc: <http://msc2010.org/resources/MSC/2010/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?early ?earlyYear
       (GROUP_CONCAT(DISTINCT STR(?kw); separator=", ") AS ?keywords)
       (GROUP_CONCAT(DISTINCT STR(?msc); separator=", ") AS ?mscs)
FROM <https://zbmath.org>
WHERE {{
  ?early dct:issued ?earlyYear ;
         schema:keywords ?kw ;
         dct:subject ?msc .

  FILTER(xsd:integer(str(?earlyYear)) < 1990)

  VALUES ?kw {{
    <https://zbmath.org/keyword/MValgebra>
    <https://zbmath.org/keyword/BCIalgebra>
    <https://zbmath.org/keyword/BCKalgebra>
    <https://zbmath.org/keyword/fuzzy_ideal>
  }}

  FILTER(
    STRSTARTS(STR(?msc), "http://msc2010.org/resources/MSC/2010/03") ||
    STRSTARTS(STR(?msc), "http://msc2010.org/resources/MSC/2010/06")
  )
}}
GROUP BY ?early ?earlyYear
ORDER BY RAND()
LIMIT 100
"""

sparql.setQuery(early_query)
early_results = sparql.query().convert()
early_ids = [res["early"]["value"] for res in early_results["results"]["bindings"]]
print (early_ids)
# import sys
# sys.exit()

# --- STEP 2: Sample later papers with MSC + keyword filter ---
later_query = f"""
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>
PREFIX msc: <http://msc2010.org/resources/MSC/2010/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?later ?laterYear
       (GROUP_CONCAT(DISTINCT STR(?kw); separator=", ") AS ?keywords)
       (GROUP_CONCAT(DISTINCT STR(?msc); separator=", ") AS ?mscs)
FROM <https://zbmath.org>
WHERE {{
  ?later dct:issued ?laterYear ;
         schema:keywords ?kw ;
         dct:subject ?msc .

  FILTER(xsd:integer(str(?laterYear)) > 2020)

  VALUES ?kw {{
    <https://zbmath.org/keyword/MValgebra>
    <https://zbmath.org/keyword/BCIalgebra>
    <https://zbmath.org/keyword/BCKalgebra>
    <https://zbmath.org/keyword/fuzzy_ideal>
  }}

  FILTER(
    STRSTARTS(STR(?msc), "http://msc2010.org/resources/MSC/2010/03") ||
    STRSTARTS(STR(?msc), "http://msc2010.org/resources/MSC/2010/06")
  )
}}
GROUP BY ?later ?laterYear
ORDER BY RAND()
LIMIT 100
"""
sparql.setQuery(later_query)
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
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX cito: <http://purl.org/spar/cito/>
PREFIX msc: <http://msc2010.org/resources/MSC/2010/>

SELECT ?early ?earlyTitle ?earlyYear ?later ?laterTitle ?laterYear
       (GROUP_CONCAT(DISTINCT ?msc; separator=",") AS ?sharedMSCs)
       (GROUP_CONCAT(DISTINCT ?kw; separator=",") AS ?sharedKeywords)
WHERE {{
  VALUES ?early {{ {early_values} }}
  VALUES ?later {{ {later_values} }}

  ?early dct:subject ?msc ;
         schema:keywords ?kw ;
         schema:name ?earlyTitle ;
         dct:issued ?earlyYear .

  ?later dct:subject ?msc ;
         schema:keywords ?kw ;
         schema:name ?laterTitle ;
         dct:issued ?laterYear .

  FILTER NOT EXISTS {{ ?later cito:cites ?early }}
}}
GROUP BY ?early ?earlyTitle ?earlyYear ?later ?laterTitle ?laterYear
HAVING(COUNT(DISTINCT ?msc) >= 1 || COUNT(DISTINCT ?kw) >= 1)
LIMIT 100
"""
sparql.setQuery(join_query)
join_results = sparql.query().convert()

# --- STEP 4: Output the results ---
for row in join_results["results"]["bindings"]:
    print(f"{row['early']['value']} {row['earlyTitle']['value']} ({row['earlyYear']['value']}) -> "
          f"{row['later']['value']} {row['laterTitle']['value']} ({row['laterYear']['value']})")
    print("Shared MSCs:", row.get("sharedMSCs", {}).get("value", ""))
    print("Shared Keywords:", row.get("sharedKeywords", {}).get("value", ""))
    print("---")
