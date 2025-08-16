import json
from tqdm import tqdm
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import DCTERMS, SKOS, FOAF, RDF, RDFS

# Files
INPUT_FILE = "records-oa-100.jsonl"
OUTPUT_FILE = "records-oa-100.ttl"

# Namespaces
ZBMATH = Namespace("https://zbmath.org/")
MSC = Namespace("http://msc2010.org/resources/MSC/2010/")
SCHEMA = Namespace("https://schema.org/")

# Graph setup
g = Graph()

g.bind("dcterms", DCTERMS)
g.bind("foaf", FOAF)
g.bind("skos", SKOS)
g.bind("msc", MSC)
g.bind("zbmath", ZBMATH)
g.bind("schema", SCHEMA) 

def make_id(text):
    return "".join(c for c in text.replace(" ", "_") if c.isalnum() or c == "_")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in tqdm(f, desc="Converting to RDF"):
        data = json.loads(line)
        identifier = data["header"]["identifier"].split(":")[-1]
        record_uri = URIRef(ZBMATH + identifier)
        metadata = data.get("metadata", {}).get("oai_zb_preview:zbmath", {})

        # Document Title
        title = metadata.get("zbmath:document_title")
        if title:
            g.add((record_uri, DCTERMS.title, Literal(title)))

        # Authors
        authors = metadata.get("zbmath:author")
        if authors:
            authors = [a.strip() for a in authors.split(";")] if isinstance(authors, str) else [authors]
            for author in authors:
                g.add((record_uri, DCTERMS.creator, Literal(author)))

        # # Author IDs
        # author_ids = metadata.get("zbmath:author_ids", {}).get("zbmath:author_id")
        # if author_ids:
        #     author_ids = [author_ids] if isinstance(author_ids, str) else author_ids
        #     for author_id in author_ids:
        #         author_uri = URIRef(ZBMATH + "authors/" + author_id)
        #         g.add((record_uri, SCHEMA.author, author_uri))

        # Document Type
        doc_type = metadata.get("zbmath:document_type")
        if doc_type:
            g.add((record_uri, DCTERMS.type, Literal(doc_type)))
        
        # uri https://zbmath.org/classification/?q=cc%3A00
        classifications = metadata.get("zbmath:classifications", {}).get("zbmath:classification")
        if classifications:
            classifications = [classifications] if isinstance(classifications, str) else classifications
            for msc in classifications:
                msc_clean = msc.strip().replace(" ", "")
                msc_uri = MSC[msc_clean]
                # msc_uri = URIRef(f"https://zbmath.org/classification/?q=cc%{msc_clean}")
                g.add((record_uri, DCTERMS.subject, msc_uri))
                g.add((msc_uri, RDF.type, SKOS.Concept))  # ✅ Explicitly say it’s a concept
                g.add((msc_uri, SKOS.prefLabel, Literal(msc_clean)))

        for keyword in metadata.get("zbmath:keywords", {}).get("zbmath:keyword", []):
            keyword = keyword.strip()
            if not keyword:
                continue
            kw_id = make_id(keyword)
            kw_uri = URIRef(f"https://zbmath.org/keyword/{kw_id}")
            g.add((record_uri, SCHEMA.keywords, kw_uri))
            g.add((kw_uri, RDF.type, SKOS.Concept))
            g.add((kw_uri, SKOS.prefLabel, Literal(keyword)))

        # Language
        lang = metadata.get("zbmath:language")
        if lang:
            g.add((record_uri, DCTERMS.language, Literal(lang)))
        # Publication Year
        pub_year = metadata.get("zbmath:publication_year")
        if pub_year:
            g.add((record_uri, DCTERMS.issued, Literal(pub_year)))

        # # Source
        # source = metadata.get("zbmath:source")
        # if source:
        #     g.add((record_uri, DCTERMS.source, Literal(source)))

        # # Spelling variants
        # spellings = metadata.get("zbmath:spelling")
        # if spellings:
        #     for spelling in [s.strip() for s in spellings.split(";")]:
        #         g.add((record_uri, RDFS.label, Literal(spelling)))

        # # Time (date of metadata creation)
        # time = metadata.get("zbmath:time")
        # if time:
        #     g.add((record_uri, DCTERMS.created, Literal(time)))

        # Zbl ID
        zbl_id = metadata.get("zbmath:zbl_id")
        if zbl_id:
            g.add((record_uri, SCHEMA.identifier, Literal(zbl_id)))

        # Review
        review = metadata.get("zbmath:review", {})
        review_text = review.get("zbmath:review_text")
        review_lang = review.get("zbmath:review_language")
        review_sign = review.get("zbmath:review_sign")
        review_type = review.get("zbmath:review_type")
        reviewer_id = review.get("zbmath:reviewer")
        if review_text:
            g.add((record_uri, SCHEMA.reviewText, Literal(review_text, lang=review_lang)))
        if review_sign:
            g.add((record_uri, SCHEMA.reviewer, Literal(review_sign)))
        if reviewer_id:
            g.add((record_uri, SCHEMA.reviewerID, Literal(reviewer_id)))
        if review_type:
            g.add((record_uri, SCHEMA.reviewType, Literal(review_type)))
        # if review_lang:
        #     g.add((record_uri, SCHEMA.reviewLanguage, Literal(review_lang)))

        # Serial info (Publisher)
        serial = metadata.get("zbmath:serial", {})
        serial_title = serial.get("zbmath:serial_title")
        serial_publisher = serial.get("zbmath:serial_publisher")
        if serial_title:
            g.add((record_uri, DCTERMS.isPartOf, Literal(serial_title)))
        if serial_publisher:
            g.add((record_uri, DCTERMS.publisher, Literal(serial_publisher)))
            
        # Pagination
        pagination = metadata.get("zbmath:pagination")
        if pagination:
            g.add((record_uri, SCHEMA.pagination, Literal(pagination)))

        # Link to resource
        link = metadata.get("zbmath:links", {}).get("zbmath:link")
        if link:
            g.add((record_uri, SCHEMA.url, URIRef(link)))

        # # Rights
        # rights = metadata.get("zbmath:rights")
        # if rights:
        #     g.add((record_uri, DCTERMS.rights, Literal(rights)))

g.bind("schema", SCHEMA, override=True)
# Save to Turtle file
g.serialize(OUTPUT_FILE, format="turtle")
print("✅ RDF triples generated to {output_file}")
