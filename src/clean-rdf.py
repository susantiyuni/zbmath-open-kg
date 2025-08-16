#clean the .ttl

import rdflib
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, FOAF, DCTERMS, SKOS
from rdflib.namespace import XSD
import re

input_file = "records-oa-100.ttl"
output_file = "records-oa-100-cleaned.ttl"

# Namespaces
MSC = Namespace("http://msc2010.org/resources/MSC/2010/")
ZBMATH = Namespace("https://zbmath.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA = Namespace("https://schema.org/")

g = rdflib.Graph()
g.parse(input_file, format="turtle")

def make_id(name):
    """Create URI-safe ID from name"""
    return re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_'))

to_add = set()
to_remove = set()

def split_names(raw_string):
    """
    Split names robustly:
    - Split on semicolon first.
    - If no semicolon, split on ' ; ' or ' ;'.
    - If only comma-separated, handle 'Surname, Name' structure safely:
        - Accept as single author if contains one comma (e.g., "Doe, John").
        - If multiple names separated by ';' or ',' at top-level, split safely.
    """
    if ';' in raw_string:
        names = [n.strip() for n in raw_string.split(';') if n.strip()]
    else:
        # Use regex to split only on semicolon or patterns like ' ; '
        names = re.split(r'\s*;\s*', raw_string)
        names = [n.strip() for n in names if n.strip()]
    return names

# Handle creators
for subj, pred, obj in g.triples((None, DCTERMS.creator, None)):
    if isinstance(obj, Literal):
        raw_names = str(obj)
        names = split_names(raw_names)
        to_remove.add((subj, pred, obj))
        for name in names:
            if not name:
                continue
            id_name = make_id(name)
            author_uri = URIRef(f"https://zbmath.org/author/{id_name}")
            to_add.add((subj, pred, author_uri))
            to_add.add((author_uri, RDF.type, FOAF.Person))
            to_add.add((author_uri, FOAF.name, Literal(name)))

# Handle publishers
for subj, pred, obj in g.triples((None, DCTERMS.publisher, None)):
    if isinstance(obj, Literal):
        raw_names = str(obj)
        names = split_names(raw_names)
        to_remove.add((subj, pred, obj))
        for name in names:
            if not name:
                continue
            id_name = make_id(name)
            pub_uri = URIRef(f"https://zbmath.org/publisher/{id_name}")
            to_add.add((subj, pred, pub_uri))
            to_add.add((pub_uri, RDF.type, FOAF.Organization))
            to_add.add((pub_uri, FOAF.name, Literal(name)))

# Handle subjects as nodes
for subj, pred, obj in g.triples((None, DCTERMS.subject, None)):
    if isinstance(obj, URIRef):
        # e.g., msc:90C22
        to_add.add((obj, RDF.type, SKOS.Concept))
        notation = obj.split("/")[-1]
        to_add.add((obj, SKOS.notation, Literal(notation)))


for subj, pred, obj in g.triples((None, DCTERMS.issued, None)):
    if isinstance(obj, Literal):
        try:
            year = int(str(obj))
            to_remove.add((subj, pred, obj))
            to_add.add((subj, pred, Literal(year, datatype=XSD.gYear)))
        except ValueError:
            pass

# Apply removals and additions
for triple in to_remove:
    g.remove(triple)
for triple in to_add:
    g.add(triple)

# Serialize the cleaned graph
g.serialize(destination=output_file, format="turtle")
print(f"✅ Cleaned RDF saved to {output_file}")
