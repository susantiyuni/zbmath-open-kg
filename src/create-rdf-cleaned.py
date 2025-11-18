"""
Convert zbMATH JSONL dump into cleaned RDF (Turtle).
"""

import json
import re
import argparse
import urllib.parse
from tqdm import tqdm
from rdflib import Graph, Literal, URIRef, Namespace, BNode
from rdflib.namespace import DCTERMS, SKOS, FOAF, RDF, XSD, RDFS


# -----------------------------
# Namespaces
# -----------------------------
ZBMATH = Namespace("https://zbmath.org/")
MSC = Namespace("http://msc2010.org/resources/MSC/2010/")
SCHEMA = Namespace("https://schema.org/")
CITO = Namespace("http://purl.org/spar/cito/")

MSC_CONCEPT = URIRef("https://zbmath.org/ontology/msc-concept")
KEYWORD_CONCEPT = URIRef("https://zbmath.org/ontology/keyword-concept")

MSC_SCHEME_URI = URIRef("https://zbmath.org/msc-scheme")
KW_SCHEME_URI = URIRef("https://zbmath.org/keyword-scheme")


# -----------------------------
# Doc type mapping
# -----------------------------
DOC_TYPE_URI_MAP = {
    "j": ("journal-article", "Journal Article"),
    "a": ("collection-article", "Collection Article"),
    "b": ("book-series", "Book Series"),
    "p": ("preprints", "Preprints")
}


# -----------------------------
# Helper functions
# -----------------------------

def make_id(text: str) -> str:
    """Convert a string into a safe compact ID."""
    if not text:
        return "unknown"
    text = text.replace(" ", "_")
    return re.sub(r"[^a-zA-Z0-9_]", "", text)


def split_names(raw):
    """Handle lists or semicolon-delimited strings."""
    if not raw:
        return []
    if isinstance(raw, list):
        raw = "; ".join([r for r in raw if r])
    return [n.strip() for n in re.split(r"\s*;\s*", raw) if n.strip()]


def safe_uri(value: str) -> URIRef:
    """Safely encode a URI, falling back to Literal if invalid."""
    if not value:
        return Literal("")
    try:
        return URIRef(urllib.parse.quote(value, safe=":/?&=%#"))
    except Exception:
        return Literal(value)


def load_msc_lookup(path: str):
    lookup = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                lookup[entry["code"]] = entry
            except Exception:
                pass
    return lookup


# -----------------------------
# Graph setup
# -----------------------------
def init_graph():
    g = Graph()
    g.bind("dcterms", DCTERMS)
    g.bind("skos", SKOS)
    g.bind("msc", MSC)
    g.bind("zbmath", ZBMATH)
    g.bind("schema", SCHEMA)
    g.bind("cito", CITO)
    g.bind("rdfs", RDFS)

    # Concept schemes
    g.add((MSC_SCHEME_URI, RDF.type, SKOS.ConceptScheme))
    g.add((MSC_SCHEME_URI, DCTERMS.title, Literal("Mathematics Subject Classification (MSC)")))
    g.add((KW_SCHEME_URI, RDF.type, SKOS.ConceptScheme))
    g.add((KW_SCHEME_URI, DCTERMS.title, Literal("zbMATH Keyword Scheme")))

    # Declare doc types
    for short, (slug, label) in DOC_TYPE_URI_MAP.items():
        uri = ZBMATH["doctype/" + slug]
        g.add((uri, RDF.type, RDFS.Class))
        g.add((uri, RDFS.label, Literal(label)))
        g.add((uri, SKOS.notation, Literal(short)))
        g.add((uri, RDFS.subClassOf, SCHEMA.ScholarlyArticle))

    # Concept classes
    g.add((MSC_CONCEPT, RDF.type, RDFS.Class))
    g.add((KEYWORD_CONCEPT, RDF.type, RDFS.Class))

    return g


# -----------------------------
# Main conversion routine
# -----------------------------
def process_record(data, g, msc_lookup):
    """Convert one JSON record into RDF."""
    doc_id = data.get("document_id", [None])[0]
    if not doc_id:
        return

    record = URIRef(ZBMATH + doc_id)

    # Basic metadata
    title = data.get("document_title", [None])[0]
    if title:
        g.add((record, DCTERMS.title, Literal(title)))
        g.add((record, SCHEMA.name, Literal(title)))

    g.add((record, RDF.type, SCHEMA.ScholarlyArticle))

    # -------- Authors --------
    authors = data.get("author", [])
    author_ids = [x for x in data.get("author_id", []) if x and x.lower() != "none"]

    if author_ids:
        for i, aid in enumerate(author_ids):
            author_uri = URIRef(f"https://zbmath.org/authors/{aid}")
            name = split_names(authors[i])[0] if i < len(authors) else aid

            g.add((record, DCTERMS.creator, author_uri))
            g.add((record, SCHEMA.author, author_uri))
            g.add((author_uri, RDF.type, SCHEMA.Person))
            g.add((author_uri, SCHEMA.name, Literal(name)))

    else:
        for raw in authors:
            for name in split_names(raw):
                aid = make_id(name)
                author_uri = URIRef(f"https://zbmath.org/author/{aid}")

                g.add((record, DCTERMS.creator, author_uri))
                g.add((record, SCHEMA.author, author_uri))
                g.add((author_uri, RDF.type, SCHEMA.Person))
                g.add((author_uri, SCHEMA.name, Literal(name)))

    # -------- Document type --------
    doc_type = data.get("document_type", [None])[0]
    if doc_type:
        info = DOC_TYPE_URI_MAP.get(doc_type.lower())
        if info:
            uri = ZBMATH["doctype/" + info[0]]
            g.add((record, DCTERMS.type, uri))

    # -------- MSC classification --------
    for code in data.get("classification", []):
        if not code:
            continue
        code = code.replace(" ", "")
        msc_uri = MSC[code]

        g.add((record, DCTERMS.subject, msc_uri))
        g.add((msc_uri, RDF.type, SKOS.Concept))
        g.add((msc_uri, SKOS.notation, Literal(code)))
        g.add((msc_uri, SKOS.inScheme, MSC_SCHEME_URI))

        info = msc_lookup.get(code, {})
        label = info.get("short_title", code)
        g.add((msc_uri, SKOS.prefLabel, Literal(label)))

    # -------- Keywords --------
    for kw in data.get("keyword", []):
        if not kw:
            continue
        kid = make_id(kw)
        kw_uri = URIRef(f"https://zbmath.org/keyword/{kid}")

        g.add((record, SCHEMA.keywords, kw_uri))
        g.add((kw_uri, RDF.type, SKOS.Concept))
        g.add((kw_uri, SKOS.prefLabel, Literal(kw)))
        g.add((kw_uri, SKOS.inScheme, KW_SCHEME_URI))

    # -------- Simple fields --------
    for key, predicate in [
        ("language", DCTERMS.language),
        ("pagination", SCHEMA.pagination)
    ]:
        val = data.get(key, [None])[0]
        if val:
            g.add((record, predicate, Literal(val)))

    # Year
    year = data.get("publication_year", [None])[0]
    if year:
        try:
            g.add((record, DCTERMS.issued, Literal(int(year), datatype=XSD.gYear)))
        except Exception:
            g.add((record, DCTERMS.issued, Literal(year)))

    # DOI / ZBL ID
    for field in ["doi", "zbl_id"]:
        val = data.get(field, [None])[0]
        if val:
            bn = BNode()
            g.add((record, SCHEMA.identifier, bn))
            g.add((bn, RDF.type, SCHEMA.PropertyValue))
            g.add((bn, SCHEMA.propertyID, Literal(field)))
            g.add((bn, SCHEMA.value, Literal(val)))

    # Links
    for link in data.get("link", []):
        if link:
            g.add((record, SCHEMA.url, safe_uri(link)))

    # Citations
    for ref in data.get("ref_id", []):
        if ref:
            g.add((record, CITO.cites, URIRef(ZBMATH + ref)))


# -----------------------------
# Main CLI entry point
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Convert JSONL → RDF Turtle")
    parser.add_argument("input", help="Input JSONL")
    parser.add_argument("output", help="Output .ttl file")
    parser.add_argument("--msc", default="msc_codes.jsonl", help="MSC lookup JSONL file")

    args = parser.parse_args()

    print("Loading MSC lookup…")
    msc_lookup = load_msc_lookup(args.msc)

    print("Initializing graph…")
    g = init_graph()

    print(f"Processing {args.input}…")
    with open(args.input, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            try:
                data = json.loads(line)
                process_record(data, g, msc_lookup)
            except Exception as e:
                print("Error:", e)

    print(f"Writing Turtle → {args.output}")
    g.serialize(destination=args.output, format="turtle")
    print("✔ Done.")


if __name__ == "__main__":
    main()
