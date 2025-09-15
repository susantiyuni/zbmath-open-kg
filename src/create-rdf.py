#convert and clean the jsonl --> rdf ttl
import json
import re
from tqdm import tqdm
from rdflib import Graph, Literal, URIRef, Namespace, BNode
from rdflib.namespace import DCTERMS, SKOS, FOAF, RDF, XSD, RDFS
import urllib.parse
import argparse

# import warnings
# warnings.filterwarnings("ignore", category=UserWarning, module="rdflib.plugins.serializers.nt")

parser = argparse.ArgumentParser(description="Convert JSONL to RDF Turtle/N-Triples")
parser.add_argument("input", help="Path to input JSONL file")
parser.add_argument("output", help="Output files")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output

# ==== NAMESPACES ====
ZBMATH = Namespace("https://zbmath.org/")
MSC = Namespace("http://msc2010.org/resources/MSC/2010/")
SCHEMA = Namespace("https://schema.org/")
CITO = Namespace("http://purl.org/spar/cito/")


# ==== GRAPH ====
g = Graph()
g.bind("dcterms", DCTERMS)
# g.bind("foaf", FOAF)
g.bind("skos", SKOS)
g.bind("msc", MSC)
g.bind("zbmath", ZBMATH)
g.bind("schema", SCHEMA)
g.bind("cito", CITO)
g.bind("rdfs", RDFS)

# ==== HELPERS ====
MSC_INFO_FILE = "msc_codes.jsonl"  # JSONL file path
msc_lookup = {}
with open(MSC_INFO_FILE, "r", encoding="utf-8") as f:
    for line in f:
        entry = json.loads(line)
        msc_lookup[entry["code"]] = entry

DOC_TYPE_URI_MAP = {
    "j": {
        "uri": ZBMATH["doctype/journal-article"],
        "label": "Journal Article"
    },
    "a": {
        "uri": ZBMATH["doctype/collection-article"],
        "label": "Collection Article"
    },
    "b": {
        "uri": ZBMATH["doctype/book-series"],
        "label": "Book Series"
    },
    "p": {
        "uri": ZBMATH["doctype/preprints"],
        "label": "Preprints"
    },
    # "t": { ... }
}

# ==== CUSTOM TYPES ====
MSC_CONCEPT = URIRef("https://zbmath.org/ontology/msc-concept")
KEYWORD_CONCEPT = URIRef("https://zbmath.org/ontology/keyword-concept")

# ==== CONCEPT SCHEMES ====
MSC_SCHEME_URI = URIRef("https://zbmath.org/msc-scheme")
KW_SCHEME_URI = URIRef("https://zbmath.org/keyword-scheme")

# Define MSC ConceptScheme
g.add((MSC_SCHEME_URI, RDF.type, SKOS.ConceptScheme))
g.add((MSC_SCHEME_URI, DCTERMS.title, Literal("Mathematics Subject Classification (MSC)")))
g.add((MSC_SCHEME_URI, RDFS.label, Literal("MSC Classification")))

# Define Keyword ConceptScheme
g.add((KW_SCHEME_URI, RDF.type, SKOS.ConceptScheme))
g.add((KW_SCHEME_URI, DCTERMS.title, Literal("zbMATH Keyword Scheme")))
g.add((KW_SCHEME_URI, RDFS.label, Literal("zbMATH Keywords")))

# === Declare Classes ===
# Custom document types
for short_code, doc_type_info in DOC_TYPE_URI_MAP.items():
    uri = doc_type_info["uri"]
    label = doc_type_info["label"]
    g.add((uri, RDF.type, RDFS.Class))
    g.add((uri, RDFS.label, Literal(label)))
    g.add((uri, SKOS.notation, Literal(short_code)))
    g.add((uri, RDFS.subClassOf, SCHEMA.ScholarlyArticle))  # NEW LINE

# Custom concept types
g.add((MSC_CONCEPT, RDF.type, RDFS.Class))
g.add((MSC_CONCEPT, RDFS.label, Literal("MSC Concept")))
g.add((KEYWORD_CONCEPT, RDF.type, RDFS.Class))
g.add((KEYWORD_CONCEPT, RDFS.label, Literal("Keyword Concept")))

g.add((SCHEMA.PropertyValue, RDF.type, RDFS.Class))
g.add((SCHEMA.PropertyValue, RDFS.label, Literal("PropertyValue")))

# Common schema classes
for class_uri, label in [
    (SCHEMA.Person, "Person"),
    (SCHEMA.Organization, "Organization"),
    (SCHEMA.Periodical, "Periodical"),
    (SCHEMA.SoftwareApplication, "Software Application"),
    (SCHEMA.Review, "Review"),
    (SCHEMA.ScholarlyArticle, "Scholarly Article")
]:
    g.add((class_uri, RDF.type, RDFS.Class))
    g.add((class_uri, RDFS.label, Literal(label)))

###

def make_id(text):
    """Create URI-safe ID from text"""
    return re.sub(r'[^a-zA-Z0-9_]', '', text.replace(" ", "_"))

def split_names(raw_string):
    """Split author/publisher names robustly"""
    if not raw_string:
        return []
    if isinstance(raw_string, list):
        raw_string = "; ".join([r for r in raw_string if r])
    return [n.strip() for n in re.split(r'\s*;\s*', raw_string) if n.strip()]

def safe_uri(uri_str):
    """Return URIRef with percent-encoding if needed"""
    encoded = urllib.parse.quote(uri_str, safe=":/?&=%#")
    return URIRef(encoded)

def to_safe_rdf_value(value):
    """Try to return a safe URIRef, fall back to Literal if not a valid URI."""
    # Attempt to detect a scheme and validate
    match = re.match(r'^([a-zA-Z][a-zA-Z0-9+.-]*):', value)
    if match:
        scheme = match.group(1)
        # If scheme is valid, try to build a URIRef
        try:
            encoded = urllib.parse.quote(value, safe=":/?&=%#")
            return URIRef(encoded)
        except Exception:
            pass
    # Otherwise, treat it as a plain literal
    return Literal(value)

# ==== STEP: LOAD JSONL AND BUILD CLEAN RDF ====
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    print (f"Start processing: {INPUT_FILE}..")
    for line in tqdm(f, desc="Building cleaned RDF"):
        try:
            data = json.loads(line)
            doc_id = data.get("document_id", [None])[0]
            if not doc_id:
                continue
            record_uri = URIRef(ZBMATH + doc_id)
            
            # Title
            title = data.get("document_title", [None])[0]
            if title and title != "None":
                g.add((record_uri, DCTERMS.title, Literal(title)))
                g.add((record_uri, SCHEMA.name, Literal(title)))
                g.add((record_uri, RDFS.label, Literal(title))) #new9/9

            # for document
            g.add((record_uri, RDF.type, SCHEMA.ScholarlyArticle))

            # Authors processing
            authors = data.get("author", [])
            author_ids = data.get("author_id", []) 
            valid_author_ids = [aid for aid in author_ids if aid and aid.lower() != "none"]
            
            # If author_ids exist, use them; otherwise, split author names
            # if author_ids and any(author_ids):
            if valid_author_ids:
                for i, aid in enumerate(author_ids):
                    if not aid or aid.lower() == "none":
                    # if not aid:
                        continue
                    # name = split_names(authors[i])[0] if i < len(authors) else aid
                    if i < len(authors):
                        raw_names = split_names(authors[i])
                        name = raw_names[0] if raw_names else aid
                    else:
                        name = aid
                    author_uri = URIRef(f"https://zbmath.org/authors/{aid}")
                    g.add((record_uri, DCTERMS.creator, author_uri))
                    g.add((record_uri, SCHEMA.author, author_uri)) #new
                    g.add((author_uri, RDF.type, SCHEMA.Person))
                    g.add((author_uri, SCHEMA.name, Literal(name)))
                    g.add((author_uri, RDFS.label, Literal(name)))  #  Add label

            else:
                # fallback: split names from author strings
                for raw in authors:
                    for name in split_names(raw):
                        id_name = make_id(name)
                        author_uri = URIRef(f"https://zbmath.org/author/{id_name}")
                        g.add((record_uri, DCTERMS.creator, author_uri))
                        g.add((record_uri, SCHEMA.author, author_uri)) #new
                        g.add((author_uri, RDF.type, SCHEMA.Person))
                        g.add((author_uri, SCHEMA.name, Literal(name)))
                        g.add((author_uri, RDFS.label, Literal(name)))  #  Add label


            doc_type_code = data.get("document_type", [None])[0]
            if doc_type_code and doc_type_code != "None":
                doc_type_info = DOC_TYPE_URI_MAP.get(doc_type_code.strip().lower())
                if doc_type_info:
                    doc_type_uri = doc_type_info["uri"]
                    g.add((record_uri, DCTERMS.type, doc_type_uri))
                else:
                    g.add((record_uri, DCTERMS.type, Literal(doc_type_code)))

            # Classifications
            classifications = data.get("classification", [])
            if classifications:
                for msc_code in classifications:
                    if not msc_code:
                        continue
                    msc_clean = msc_code.strip().replace(" ", "")
                    
                    msc_uri = MSC[msc_clean]
                    g.add((record_uri, DCTERMS.subject, msc_uri))
                    g.add((msc_uri, RDF.type, SKOS.Concept))
                    g.add((msc_uri, RDF.type, MSC_CONCEPT))
                    g.add((msc_uri, SKOS.notation, Literal(msc_clean)))
                    
                    # Use short title as prefLabel if available, otherwise fallback to code
                    msc_info = msc_lookup.get(msc_clean)
                    label = msc_info.get("short_title") if msc_info and msc_info.get("short_title") else msc_clean
                    g.add((msc_uri, SKOS.prefLabel, Literal(label)))
                    g.add((msc_uri, SKOS.inScheme, MSC_SCHEME_URI))
                    g.add((msc_uri, RDFS.label, Literal(label)))
                    
                    # Add zbMATH URL if available
                    if msc_info:
                        zb_url = msc_info.get("zbmath_url")
                        if zb_url:
                            # g.add((msc_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#seeAlso"), URIRef(zb_url)))
                            g.add((msc_uri, RDFS.seeAlso, URIRef(safe_uri(zb_url))))

            # Keywords
            keywords = data.get("keyword", [])
            if keywords:
                for kw in keywords:
                    if not kw:
                        continue
                    kw_id = make_id(kw)
                    kw_uri = URIRef(f"https://zbmath.org/keyword/{kw_id}")
                    g.add((record_uri, SCHEMA.keywords, kw_uri))
                    g.add((kw_uri, RDF.type, SKOS.Concept))
                    g.add((kw_uri, RDF.type, KEYWORD_CONCEPT))  # 
                    g.add((kw_uri, SKOS.prefLabel, Literal(kw)))
                    g.add((kw_uri, RDFS.label, Literal(kw)))  # 
                    g.add((kw_uri, SKOS.inScheme, KW_SCHEME_URI))
                    g.add((kw_uri, RDFS.label, Literal(kw)))

            # Language
            lang = data.get("language", [None])[0]
            if lang and lang != "None":
                g.add((record_uri, DCTERMS.language, Literal(lang)))

            # Publication year
            pub_year = data.get("publication_year", [None])[0]
            if pub_year and pub_year != "None":
                try:
                    g.add((record_uri, DCTERMS.issued, Literal(int(pub_year), datatype=XSD.gYear)))
                    g.add((record_uri, SCHEMA.datePublished, Literal(int(pub_year), datatype=XSD.gYear)))
                except ValueError:
                    g.add((record_uri, DCTERMS.issued, Literal(pub_year)))
                    g.add((record_uri, SCHEMA.datePublished, Literal(pub_year)))

            # Pagination
            pagination = data.get("pagination", [None])[0]
            if pagination and pagination != "None":
                g.add((record_uri, SCHEMA.pagination, Literal(pagination)))

            # Zbl ID
            zbl_id = data.get("zbl_id", [None])[0]
            if zbl_id and zbl_id != "None":
                zbl_bn = BNode()
                g.add((record_uri, SCHEMA.identifier, zbl_bn))
                g.add((zbl_bn, RDF.type, SCHEMA.PropertyValue))
                g.add((zbl_bn, SCHEMA.propertyID, Literal("zbl_id")))
                g.add((zbl_bn, SCHEMA.value, Literal(zbl_id)))
            
            # doi
            doi = data.get("doi", [None])[0]
            if doi and doi != "None":
                doi_bn = BNode()
                g.add((record_uri, SCHEMA.identifier, doi_bn))
                g.add((doi_bn, RDF.type, SCHEMA.PropertyValue))
                g.add((doi_bn, SCHEMA.propertyID, Literal("doi")))
                g.add((doi_bn, SCHEMA.value, Literal(doi)))

            # # Review
            # Review block (refactored as schema:Review entity)
            review_text = data.get("review_text", [None])[0]
            review_sign = data.get("review_sign", [None])[0]
            reviewer_id = data.get("reviewer_id", [None])[0]
            review_type = data.get("review_type", [None])[0]
            review_lang = data.get("review_language", [None])[0]

            if any([review_text, reviewer_id, review_sign]) and review_text != "None":
                review_node = BNode()
                g.add((record_uri, SCHEMA.review, review_node))
                g.add((review_node, RDF.type, SCHEMA.Review))

                # Review body
                if review_text and review_text != "None":
                    g.add((review_node, SCHEMA.reviewBody, Literal(review_text)))

                # Review language
                if review_lang and review_lang != "None":
                    g.add((review_node, SCHEMA.inLanguage, Literal(review_lang)))

                # Review type
                if review_type and review_type != "None":
                    g.add((review_node, SCHEMA.reviewAspect, Literal(review_type)))

                # Reviewer
                if reviewer_id and reviewer_id != "None":
                    # reviewer_uri = URIRef(f"https://zbmath.org/reviewers/{make_id(reviewer_id)}")
                    reviewer_uri = URIRef(f"https://zbmath.org/authors/{reviewer_id}")
                    g.add((review_node, SCHEMA.reviewer, reviewer_uri))  # instead of SCHEMA.author
                    g.add((reviewer_uri, RDF.type, SCHEMA.Person))
                    
                    # Use review_sign as name if available
                    if review_sign and review_sign != "None":
                        g.add((reviewer_uri, SCHEMA.name, Literal(review_sign)))
                        g.add((reviewer_uri, RDFS.label, Literal(name)))  #  Add label
                    else:
                        g.add((reviewer_uri, SCHEMA.name, Literal(reviewer_id)))
                        g.add((reviewer_uri, RDFS.label, Literal(reviewer_id)))  #  Add label

            # Software
            software_names = data.get("software_name", [])
            sw_ids = data.get("swmath_id", [])
            
            for name, sw_id in zip(software_names, sw_ids):
                if sw_id and sw_id != "None":
                    software_uri = URIRef(f"https://zbmath.org/software/{sw_id}")
                    g.add((software_uri, RDF.type, SCHEMA.SoftwareApplication))
                    if name and name != "None":
                        g.add((software_uri, SCHEMA.name, Literal(name)))
                        g.add((software_uri, RDFS.label, Literal(name)))  # 
                    g.add((software_uri, SCHEMA.identifier, Literal(sw_id)))
            
                    # Link software to the article
                    g.add((record_uri, SCHEMA.software, software_uri))
                    g.add((software_uri, SCHEMA.isPartOf, record_uri)) #reversible


            # Serial / Publisher
            serial_title = data.get("serial_title", [None])[0]
            if serial_title and serial_title != "None":
                journal_id = make_id(serial_title)
                journal_uri = URIRef(f"https://zbmath.org/journal/{journal_id}")
                g.add((record_uri, DCTERMS.isPartOf, journal_uri))
                g.add((journal_uri, RDF.type, SCHEMA.Periodical))
                g.add((journal_uri, SCHEMA.name, Literal(serial_title)))
                g.add((journal_uri, RDFS.label, Literal(serial_title)))  # 

                # Optional: if ISSN is known, add it here
                # g.add((journal_uri, SCHEMA.issn, Literal("xxxx-xxxx")))

            serial_publisher = data.get("serial_publisher", [None])[0]
            if serial_publisher and serial_publisher != "None":
                for name in split_names(serial_publisher):
                    id_name = make_id(name)
                    pub_uri = URIRef(f"https://zbmath.org/publisher/{id_name}")
                    g.add((record_uri, DCTERMS.publisher, pub_uri))
                    g.add((pub_uri, RDF.type, SCHEMA.Organization))
                    g.add((pub_uri, SCHEMA.name, Literal(name)))
                    g.add((pub_uri, RDFS.label, Literal(name)))  # 
            
            # Links (flat list now)
            link_data = data.get("link", [])
            if link_data:
                if isinstance(link_data, str):
                    links = [link_data]
                else:
                    links = list(link_data)
                for l in links:
                    if not l:
                        continue
                    g.add((record_uri, SCHEMA.url, to_safe_rdf_value(l)))
                    

            # --- Citation Network ---
            for cited_id in data.get("ref_id", []):
                if cited_id and cited_id != "None":
                    cited_uri = URIRef(ZBMATH + cited_id)
                    g.add((record_uri, CITO.cites, cited_uri))
                    # g.add((cited_uri, RDF.type, SCHEMA.ScholarlyArticle))

        except Exception as e:
            print(f"⚠️ Error processing record: {e}{line}")
            continue

# ==== SAVE FINAL CLEAN RDF ====

# print(f"Serializing (nt)..")
# g.serialize(destination=OUTPUT_FILE_2, format="nt")
# print(f"✅ RDF (nt) saved to {OUTPUT_FILE_2}")

print(f"Serializing (ttl)..")
g.serialize(destination=OUTPUT_FILE, format="turtle")
print(f"✅ RDF (ttl) saved to {OUTPUT_FILE}")
