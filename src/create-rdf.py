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

parser = argparse.ArgumentParser(description="Convert JSONL to RDF Turtle and N-Triples")
parser.add_argument("input", help="Path to input JSONL file")
parser.add_argument("output", help="Base path for output files (without extension)")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = f"out-ttl-new/{args.output}.ttl"
OUTPUT_FILE_2 = f"out-nt-new/{args.output}.nt"

# # ==== FILES ====

# INPUT_FILE = "out/out-4ab.jsonl"
# OUTPUT_FILE = "out-nt/out4-ab.ttl"
# OUTPUT_FILE_2 = "out-nt/out-4ab.nt"

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

# ==== CUSTOM TYPES ====
MSC_CONCEPT = URIRef("https://zbmath.org/ontology/MSCConcept")
KEYWORD_CONCEPT = URIRef("https://zbmath.org/ontology/KeywordConcept")

# ==== HELPERS ====

MSC_INFO_FILE = "msc_codes.jsonl"  # JSONL file path

msc_lookup = {}
with open(MSC_INFO_FILE, "r", encoding="utf-8") as f:
    for line in f:
        entry = json.loads(line)
        msc_lookup[entry["code"]] = entry

# msc_clean = "34B27"
# msc_info = msc_lookup.get(msc_clean)
# label = msc_info.get("short_title") if msc_info and msc_info.get("short_title") else msc_clean

# print (label)
# sys.exit

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
    # try:
    #     return URIRef(uri_str)
    # except Exception:
    #     encoded = urllib.parse.quote(uri_str, safe=":/?&=%#")
    #     return URIRef(encoded)
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

            # for document
            g.add((record_uri, RDF.type, SCHEMA.ScholarlyArticle))

            # Title
            title = data.get("document_title", [None])[0]
            if title:
                g.add((record_uri, DCTERMS.title, Literal(title)))
                g.add((record_uri, SCHEMA.name, Literal(title)))

            # Authors processing
            authors = data.get("author", [])
            author_ids = data.get("author_id", [])
            
            # If author_ids exist, use them; otherwise, split author names
            if author_ids and any(author_ids):
                for i, aid in enumerate(author_ids):
                    if not aid:
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
                    # g.add((author_uri, RDF.type, FOAF.Person))
                    # g.add((author_uri, FOAF.name, Literal(name)))
                    g.add((author_uri, RDF.type, SCHEMA.Person))
                    g.add((author_uri, SCHEMA.name, Literal(name)))
                    

            else:
                # fallback: split names from author strings
                for raw in authors:
                    for name in split_names(raw):
                        id_name = make_id(name)
                        author_uri = URIRef(f"https://zbmath.org/author/{id_name}")
                        g.add((record_uri, DCTERMS.creator, author_uri))
                        g.add((record_uri, SCHEMA.author, author_uri)) #new
                        # g.add((author_uri, RDF.type, FOAF.Person))
                        # g.add((author_uri, FOAF.name, Literal(name)))
                        g.add((author_uri, RDF.type, SCHEMA.Person))
                        g.add((author_uri, SCHEMA.name, Literal(name)))

            # Document type
            doc_type = data.get("document_type", [None])[0]
            if doc_type:
                g.add((record_uri, DCTERMS.type, Literal(doc_type)))

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
                    g.add((msc_uri, RDF.type, MSC_CONCEPT))  # 🆕 Add specific type
                    g.add((msc_uri, SKOS.notation, Literal(msc_clean)))
                    
                    # Use short title as prefLabel if available, otherwise fallback to code
                    msc_info = msc_lookup.get(msc_clean)
                    label = msc_info.get("short_title") if msc_info and msc_info.get("short_title") else msc_clean
                    g.add((msc_uri, SKOS.prefLabel, Literal(label)))
                    
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
                    g.add((kw_uri, RDF.type, KEYWORD_CONCEPT))  # 🆕
                    g.add((kw_uri, SKOS.prefLabel, Literal(kw)))

            # Language
            lang = data.get("language", [None])[0]
            if lang:
                g.add((record_uri, DCTERMS.language, Literal(lang)))

            # Publication year
            pub_year = data.get("publication_year", [None])[0]
            if pub_year:
                try:
                    g.add((record_uri, DCTERMS.issued, Literal(int(pub_year), datatype=XSD.gYear)))
                    g.add((record_uri, SCHEMA.datePublished, Literal(int(pub_year), datatype=XSD.gYear)))
                except ValueError:
                    g.add((record_uri, DCTERMS.issued, Literal(pub_year)))
                    g.add((record_uri, SCHEMA.datePublished, Literal(pub_year)))

            # Pagination
            pagination = data.get("pagination", [None])[0]
            if pagination:
                g.add((record_uri, SCHEMA.pagination, Literal(pagination)))

            # Zbl ID
            zbl_id = data.get("zbl_id", [None])[0]
            # if zbl_id:
            #     g.add((record_uri, SCHEMA.identifier, Literal(zbl_id)))
            if zbl_id:
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
            # review_text = data.get("review_text", [None])[0]
            # if review_text and review_text != "None":
            #     g.add((record_uri, SCHEMA.reviewText, Literal(review_text)))
            
            # review_sign = data.get("review_sign", [None])[0]
            # if review_sign and review_sign != "None":
            #     g.add((record_uri, SCHEMA.reviewer, Literal(review_sign)))
            
            # reviewer_id = data.get("reviewer", [None])[0]
            # if reviewer_id and reviewer_id != "None":
            #     g.add((record_uri, SCHEMA.reviewerID, Literal(reviewer_id)))
            
            # review_type = data.get("review_type", [None])[0]
            # if review_type and review_type != "None":
            #     g.add((record_uri, SCHEMA.reviewType, Literal(review_type)))

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
                    reviewer_uri = URIRef(f"https://zbmath.org/reviewer/{make_id(reviewer_id)}")
                    g.add((review_node, SCHEMA.author, reviewer_uri))
                    # g.add((reviewer_uri, RDF.type, FOAF.Person)) #changed
                    g.add((reviewer_uri, RDF.type, SCHEMA.Person))
                    
                    # Use review_sign as name if available
                    if review_sign and review_sign != "None":
                        # g.add((reviewer_uri, FOAF.name, Literal(review_sign))) #changed
                        g.add((reviewer_uri, SCHEMA.name, Literal(review_sign)))
                    else:
                        # g.add((reviewer_uri, FOAF.name, Literal(reviewer_id))) #changed
                        g.add((reviewer_uri, SCHEMA.name, Literal(reviewer_id)))

            # Software
            software_names = data.get("software_name", [])
            sw_ids = data.get("swmath_id", [])
            
            for name, sw_id in zip(software_names, sw_ids):
                if sw_id and sw_id != "None":
                    software_uri = URIRef(f"https://zbmath.org/software/{sw_id}")
                    g.add((software_uri, RDF.type, SCHEMA.SoftwareApplication))
                    if name and name != "None":
                        g.add((software_uri, SCHEMA.name, Literal(name)))
                    g.add((software_uri, SCHEMA.identifier, Literal(sw_id)))
            
                    # Link software to the article
                    g.add((record_uri, SCHEMA.software, software_uri))
                    # g.add((software_uri, SCHEMA.isPartOf, record_uri)) #reversible


            # Serial / Publisher
            # serial_title = data.get("serial_title", [None])[0]
            # if serial_title and serial_title != "None":
            #     g.add((record_uri, DCTERMS.isPartOf, Literal(serial_title)))
            serial_title = data.get("serial_title", [None])[0]
            if serial_title and serial_title != "None":
                journal_id = make_id(serial_title)
                journal_uri = URIRef(f"https://zbmath.org/journal/{journal_id}")
                g.add((record_uri, DCTERMS.isPartOf, journal_uri))
                g.add((journal_uri, RDF.type, SCHEMA.Periodical))
                g.add((journal_uri, SCHEMA.name, Literal(serial_title)))

                # Optional: if ISSN is known, add it here
                # g.add((journal_uri, SCHEMA.issn, Literal("xxxx-xxxx")))

            serial_publisher = data.get("serial_publisher", [None])[0]
            if serial_publisher and serial_publisher != "None":
                for name in split_names(serial_publisher):
                    id_name = make_id(name)
                    pub_uri = URIRef(f"https://zbmath.org/publisher/{id_name}")
                    # g.add((record_uri, DCTERMS.publisher, pub_uri))
                    # g.add((pub_uri, RDF.type, FOAF.Organization))
                    # g.add((pub_uri, FOAF.name, Literal(name)))
                    # 🔍 Publisher as schema:Organization
                    g.add((record_uri, DCTERMS.publisher, pub_uri))
                    g.add((pub_uri, RDF.type, SCHEMA.Organization))
                    g.add((pub_uri, SCHEMA.name, Literal(name)))
            
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
                    # g.add((record_uri, SCHEMA.url, safe_uri(l)))
                    # g.add((record_uri, SCHEMA.url, Literal(safe_uri(l))))
                    g.add((record_uri, SCHEMA.url, to_safe_rdf_value(l)))
                    

            # --- Citation Network ---
            for cited_id in data.get("ref_id", []):
                if cited_id:
                    cited_uri = URIRef(ZBMATH + cited_id)
                    g.add((record_uri, CITO.cites, cited_uri))

        except Exception as e:
            print(f"⚠️ Error processing record: {e}{line}")
            continue

# ==== SAVE FINAL CLEAN RDF ====
print(f"Serializing (ttl)..")
g.serialize(destination=OUTPUT_FILE, format="turtle")
print(f"✅ RDF (ttl) saved to {OUTPUT_FILE}")

print(f"Serializing (nt)..")
g.serialize(destination=OUTPUT_FILE_2, format="nt")
print(f"✅ RDF (nt) saved to {OUTPUT_FILE_2}")
