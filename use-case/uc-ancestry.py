from SPARQLWrapper import SPARQLWrapper, JSON

# --- CONFIGURATION ---
endpoint_url = "http://localhost:8890/sparql"  # Virtuoso SPARQL endpoint

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
    # <https://zbmath.org/keyword/cohomology>
    <https://zbmath.org/keyword/spectral_sequences>
  }}

  FILTER(
    STRSTARTS(STR(?msc), "http://msc2010.org/resources/MSC/2010/55")
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
    # <https://zbmath.org/keyword/cohomology>
    <https://zbmath.org/keyword/spectral_sequences>
  }}

  FILTER(
    STRSTARTS(STR(?msc), "http://msc2010.org/resources/MSC/2010/18G")
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

SELECT ?early ?earlyTitle ?earlyYear ?earlyMSC 
      ?later ?laterTitle ?laterYear ?laterMSC 
       (GROUP_CONCAT(DISTINCT ?kw; separator=",") AS ?sharedKeywords)

# SELECT ?early ?earlyTitle ?earlyYear ?later ?laterTitle ?laterYear
#        (GROUP_CONCAT(DISTINCT ?msc; separator=",") AS ?sharedMSCs)
#        (GROUP_CONCAT(DISTINCT ?kw; separator=",") AS ?sharedKeywords)
WHERE {{
  VALUES ?early {{ {early_values} }}
  VALUES ?later {{ {later_values} }}

  ?early dct:subject ?earlyMSC ;
         schema:keywords ?kw ;
         schema:name ?earlyTitle ;
         dct:issued ?earlyYear .

  ?later dct:subject ?laterMSC ;
         schema:keywords ?kw ;
         schema:name ?laterTitle ;
         dct:issued ?laterYear .

  FILTER NOT EXISTS {{ ?later cito:cites ?early }}
}}
GROUP BY ?early ?earlyTitle ?earlyYear ?later ?laterTitle ?laterYear ?earlyMSC ?laterMSC
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
