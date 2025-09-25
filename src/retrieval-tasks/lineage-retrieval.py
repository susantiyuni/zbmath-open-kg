from SPARQLWrapper import SPARQLWrapper, JSON

# --- Configuration ---
endpoint = "http://localhost:8890/sparql"
sparql = SPARQLWrapper(endpoint)
sparql.setReturnFormat(JSON)

# --- Step 1: Authored Papers ---
authored_query = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX zbmath: <https://zbmath.org/>

SELECT DISTINCT ?authored ?aTitle ?aYear ?aMSC ?kw ?kwLabel
WHERE {
  ?authored a schema:ScholarlyArticle ;
            schema:author <https://zbmath.org/authors/bodlaender.hans-l> ;
            dcterms:title ?aTitle ;
            dcterms:issued ?aYear ;
            dcterms:subject ?aMSC ;
            schema:keywords ?kw .
    
  OPTIONAL { ?kw skos:prefLabel ?kwLabel }
  
  FILTER(STRSTARTS(STR(?aMSC), "http://msc2010.org/resources/MSC/2010/68"))
  FILTER(xsd:integer(STR(?aYear)) > 2000 && xsd:integer(STR(?aYear)) <= 2025)

}
# ORDER BY RAND()
ORDER BY DESC(?rYear)
LIMIT 1000
"""
sparql.setQuery(authored_query)
authored_results = sparql.query().convert()

authored_papers = {}
for res in authored_results["results"]["bindings"]:
    pid = res["authored"]["value"]
    title = res["aTitle"]["value"]
    year = int(res["aYear"]["value"])
    msc = res.get("aMSC", {}).get("value", "")
    kw = res.get("kw", {}).get("value", "")
    kwLabel = res.get("kwLabel", {}).get("value", "")
    if pid not in authored_papers:
        authored_papers[pid] = {"title": title, "year": year, "msc": msc, "keywords": set(), "kwlabels": set()}
    authored_papers[pid]["keywords"].add(kw)
    if kwLabel:
        authored_papers[pid]["kwlabels"].add(kwLabel)

# print (authored_papers)
# sys.exit()

# --- Step 2: Reviewed Papers ---
reviewed_query = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX zbmath: <https://zbmath.org/>

SELECT DISTINCT ?reviewed ?rTitle ?rYear ?rMSC ?kw ?kwLabel
WHERE {
  ?reviewed a schema:ScholarlyArticle ;
            schema:review ?rev ;
            dcterms:title ?rTitle ;
            dcterms:issued ?rYear ;
            dcterms:subject ?rMSC ;
            schema:keywords ?kw .
  
  ?rev schema:reviewer<https://zbmath.org/authors/bodlaender.hans-l> .
  
  OPTIONAL { ?kw skos:prefLabel ?kwLabel }

  FILTER(STRSTARTS(STR(?rMSC), "http://msc2010.org/resources/MSC/2010/05"))
  # FILTER(xsd:integer(STR(?rYear)) >= 1980 && xsd:integer(STR(?rYear)) <= 2000)
  FILTER(xsd:integer(STR(?rYear)) <= 2000)

}
# ORDER BY ASC(?rYear)
ORDER BY RAND()
LIMIT 1000

"""
sparql.setQuery(reviewed_query)
reviewed_results = sparql.query().convert()

reviewed_papers = {}
for res in reviewed_results["results"]["bindings"]:
    pid = res["reviewed"]["value"]
    title = res["rTitle"]["value"]
    year = int(res["rYear"]["value"])
    msc = res.get("rMSC", {}).get("value", "")
    kw = res.get("kw", {}).get("value", "")
    kwLabel = res.get("kwLabel", {}).get("value", "")
    if pid not in reviewed_papers:
        reviewed_papers[pid] = {"title": title, "year": year, "msc": msc, "keywords": set(), "kwlabels": set()}
    reviewed_papers[pid]["keywords"].add(kw)
    if kwLabel:
        reviewed_papers[pid]["kwlabels"].add(kwLabel)

# --- Step 3: Link Authored + Reviewed via Shared Keywords ---
print("Counting linked papers (reviewed → authored with shared keywords):\n")

linked_count = 0

for r_id, r_data in reviewed_papers.items():
    for a_id, a_data in authored_papers.items():
        if r_id == a_id:
            continue
        if a_data["year"] <= r_data["year"]:
            continue
        shared = r_data["keywords"].intersection(a_data["keywords"])
        if len(shared) > 1:
            linked_count += 1
            # If you want, you can still print details here, or comment it out:
            print(f"[{r_data['year']}] {r_data['title']} {r_data['msc']}\n  ↳ [{a_data['year']}] {a_data['title']} {a_data['msc']}")
            print(f"  Shared keywords ({len(shared)}): {', '.join(shared)}")
            print("-" * 60)

print(f"Total linked paper pairs: {linked_count}")
