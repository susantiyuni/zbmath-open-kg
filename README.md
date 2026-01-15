# Historically-Grounded Retrieval of Scholarly Research Beyond Citation

We propose **historically-grounded retrieval**, a new paradigm for scholarly IR that shifts focus from popularity-based citation metrics to the historical and conceptual development of knowledge. To enable this, we built a large-scale, historically comprehensive knowledge graph from **zbMATH Open**, covering centuries of mathematical research. 

Built on the proposed paradigm and infrastructure, we formalize and implement four new IR tasks:  

- **Precursor Retrieval** — identifying overlooked works beyond citations  
- **Conceptual Ancestry** — tracing concept migration across (sub)fields  
- **Revival Detection** — spotting re-emerging ideas in new contexts  
- **Reviewer–Author Lineage** — mapping intellectual transmission via scholarly interactions  

---

## zbMATH Knowledge Graph: Key Statistics (as of August 2025)
- **Temporal Span**: 1763~2025. See ([`src/retrieval-tasks/year-count.tsv`](./src/retrieval-tasks/year-count.tsv)) for the per-year distribution.  
- **Triples**: 159M+
- **Distinct Entities**: 36M+
- **Publications**: 4M+
- **Disambiguated Authors/Reviewers**: 1M+
- **Reviews**: 3M+
- **Subject Classifications (MSC)**: 6,500+
- **Keywords**: 3M+
- **Software**: 30k+ ... (and more)

## zbMATH Knowledge Graph: Key Features

- **RDF-Based Semantic Knowledge Graph**  
  Compliant with RDF and Semantic Web standards, the zbMATH Open KG is built entirely from RDF triples using widely adopted ontologies and vocabularies (e.g., ``schema:, dcterms:, skos:, cito:``), supporting semantic interoperability and adheres to Linked Open Data principles. The full RDF dumps will be published on [**Zenodo**](http://zenodo) after the anonymous review period concludes. A sample of 200 records is available here: [`data/subset-200.ttl`](./data/subset-200.ttl). 

- **Expert-Curated, High-Quality Mathematical Metadata**  
  In addition to standard bibliographic metadata, it incorporates annotated mathematical publications with expert-curated reviews and keywords, disambiguated authors, and *Mathematics Subject Classification* (MSC) codes — a fine-grained ontology for math subject classification.

- **Historically-Grounded Intellectual Discovery**  
  Its comprehensive and long-term coverage enable long-range intellectual analysis such as historically-grounded retrieval tasks e.g., identifying overlooked precursors and tracing conceptual lineages across (_sub_)disciplines.

- **SPARQL Query Interface**  
  A SPARQL endpoint (temporarily at [**SPARQL endpoint url**](http://212.227.170.235:8890/sparql)) for directly executing queries over the KG.
  
- **Linked Data Integration**  
Cross-links with external URLs and persistent identifiers (e.g., DOI).
  
## zbMATH Knowledge Graph: Construction and Setup

### Prerequisites

- Python 3.12+  
- Python libraries: `rdflib`, `SPARQLWrapper`, and others (see requirements.txt)  
- Java 8 or higher (required only if you run Apache Jena libraries outside Docker)  
- Docker (for running RDF triple stores like Apache Jena Fuseki without manual Java setup)  
  - We use [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) as an example for its simplicity  
  - *Note:* Production SPARQL endpoints use Virtuoso (See the [`zb-virtuoso`](./zb-virtuoso) directory for the complete Virtuoso setup.)

### Data Harvesting

To harvest data by zbMATH ID (e.g., ID list of zbMATH open access subset: [zbMATH OA subset](https://zenodo.org/records/8021789)), run:

```bash
python harvest-by-id.py 
```

For bulk download (via _sickle_), refers to: [zbMATHOpen Harvester](https://github.com/zbMATHOpen/mscHarvester)

### RDF Construction

Using raw `.jsonl` zbMATH data obtained from the API (see example: [`data/subset-200.jsonl`](./data/subset-200.jsonl)), run the following commands to automatically generate the RDF KG:

```bash
# Option 1: Run the Python script
python create-rdf.py data/subset-200.jsonl subset-200

# Option 2: Run the shell script for batch processing
run-convert.sh

```

### RDF Triple Store Setup

We provide example using [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) as the RDF triple store for the KG. Fuseki provides a lightweight SPARQL server to host and query your knowledge graph. The example setup is provided in [`front/`](./front). 

We provide a sample subset of the zbMATH Open KG data you can use here: [`data/subset-200.ttl`](./data/subset-200.ttl). Before running the example, ensure this initial data file is located in the same folder as the `docker-compose.yml` file. If not, update the volume mapping in [`front/docker-compose.yml`](./front/docker-compose.yml) accordingly:

```yaml
- ./subset-200.ttl:/data.ttl
```

Then, start the service by running:
```bash
docker compose up -d
```

This will launch Fuseki on port 3030 and load the initial data via [`fuseki-entrypoint.sh`](front/fuseki-entrypoint.sh).

Your SPARQL endpoint URL will be available at: `http://localhost:3030/dataset/sparql`

For Virtuoso setup, see the [`zb-virtuoso`](./zb-virtuoso) directory.

## Historically-Grounded Retrieval Implementation

First, install the prerequisite libraries:

```bash
pip install -r requirements.txt
```

Next, configure the SPARQL endpoint url in the script to match your KG's SPARQL endpoint.

```
# --- CONFIGURATION ---
endpoint_url = "http://localhost:8890/sparql"  # change into your SPARQL endpoint
```

Run the following scripts ([`src/retrieval-tasks/`](./src/retrieval-tasks/)) to perform the respective retrieval tasks:

- **(1) Precursor Retrieval**  
  Identify overlooked foundational works beyond citation metrics.
  
  To get potential precursor–successor pairs based on shared concepts, run:
  ```bash
  python precursor-retrieval.py
  ```
  To list all potential precursors of a specific article (e.g., id=7309918), run the following query on your SPARQL endpoint.
  ```
  precursor-id7309918.sparql
  ```
- **(2) Conceptual Ancestry**  
 Trace the migration of concepts across disciplines and subfields.  
  ```bash
  python ancestry-retrieval.py
  ```
- **(3) Revival Detection**  
  Detect ideas that are re-emerging in new contexts or domains.  
  ```bash
  python revival-retrieval.py
  ```
- **(4) Reviewer–Author Lineage**  
  Map intellectual transmission through scholarly interactions (author-reviewer relationship) 
  ```bash
  python lineage-retrieval.py
  ```


## Repository Structure

- [`data/`](./data) – `.jsonl` raw data and `.ttl` RDF KG (subset), ontology files (`.ttl`), etc.
- [`front/`](./front) – Fuseki triple store setup for serving the RDF subset (example only — SPARQL endpoint runs on Virtuoso for scalability)
- [`src/`](./src) – Source code for KG construction (data harvest, statistics calculation, RDF transformation, etc).
- [`src/retrieval-tasks/`](./src/retrieval-tasks/) – Source code and SPARQL queries for historically-grounded retrieval tasks.
- [`use-case/`](./use-case) – Use case-specific results and visualizations
- [`run-convert.sh`](./run-convert.sh) – Shell script to convert raw data into RDF format
- [`README.md`](./README.md) – Project documentation


### License

All content generated by zbMATH Open KG are distributed under [CC-BY-SA 4.0.](https://creativecommons.org/licenses/by-sa/4.0/), in accordance with the specification at [zbMATH Open OAI-PMH API](https://oai.zbmath.org/):
```
Content generated by zbMATH Open, such as reviews, classifications, software, or author disambiguation data,are distributed under CC-BY-SA 4.0.
This defines the license for the whole dataset, which also contains non-copyrighted bibliographic metadata and reference data derived from I4OC (CC0).
Note that the API only provides a subset of the data in the zbMATH Open Web interface.
In several cases, third-party information, such as abstracts, cannot be made available under a suitable license through the API.
In those cases, we replaced the data with the string "zbMATH Open Web Interface contents unavailable due to conflicting licenses."
```

📧 Contact: yuni.susanti@fiz-karlsruhe.de
