# Historically-Grounded Retrieval of Scholarly Research Beyond Citation

We propose **historically-grounded retrieval**, a new paradigm for scholarly IR that shifts focus from popularity-based citation metrics to the historical and conceptual development of knowledge. To enable this, we built a large-scale, historically comprehensive knowledge graph from **zbMATH Open**, covering 250 years of mathematical research. 

Built on the proposed paradigm and infrastructure, we formalize and implement four new IR tasks:  

- **Precursor Retrieval** — identifying overlooked works beyond citations  
- **Conceptual Ancestry** — tracing concept migration across (sub)fields  
- **Revival Detection** — spotting re-emerging ideas in new contexts  
- **Reviewer–Author Lineage** — mapping intellectual transmission via scholarly interactions  

---

## 📊 zbMATH Knowledge Graph: Key Statistics
- **Triples**: 159M+
- **Distinct Entities**: 36M+
- **Publications**: 4M+
- **Authors/Reviewers**: 1M+
- **Reviews**: 3M+
- **Subject Classifications (MSC)**: 6,500+
- **Keywords**: 3M+
- **Software**: 30k+ ... (and more)

## 📌 zbMATH Knowledge Graph: Key Features

- 🧠 **RDF-Based Semantic Knowledge Graph**  
  Fully compliant with RDF and Semantic Web standards, the zbMATH Open KG is built entirely from RDF triples using widely adopted ontologies and vocabularies. It supports semantic interoperability and adheres to Linked Open Data principles, enabling rich, machine-readable knowledge representation. The full RDF dumps will be published on [**Zenodo**](http://zenodo) after the anonymous review period concludes. A sample of 200 records is available here: [`data/subset-200.ttl`](./data/subset-200.ttl). 

- 📚 **Expert-Curated, High-Quality Mathematical Metadata**  
  Integrates richly annotated publications, disambiguated authors, expert reviews, keywords, and *Mathematics Subject Classification* (MSC) — a historically stable, fine-grained ontology — enabling nuanced exploration beyond citations.

- 📈 **Historically-Grounded Intellectual Discovery**  
  Enables historically-grounded retrieval and long-range intellectual analysis, e.g., for uncovering overlooked precursors, tracing conceptual lineages and revivals, and mapping intellectual influence across disciplines.

- 🔍 **SPARQL Query Interface**  
  A SPARQL endpoint (temporarily at [**SPARQL endpoint url**](http://212.227.170.235:8890/sparql)) for directly executing complex queries.
  
- 🔄 **Linked Data Integration**  
Cross-links with authoritative external URL and identifiers (e.g., DOI), enhancing entity resolution and connecting the KG within the broader scholarly data ecosystem.

## 📁 Repository Structure

- [`data/`](./data) – `.jsonl` raw data and `.ttl` RDF KG (subset), ontology files (`.ttl`), etc.
- [`front/`](./front) – Fuseki triple store setup for serving the RDF subset (example only — SPARQL endpoint runs on Virtuoso for scalability)
- [`src/`](./src) – Source code for data harvest, RDF KG construction, statistics calculation, etc.
- [`use-case/`](./use-case) – Use case-specific code, SPARQL queries, results, and visualizations
- [`run-convert.sh`](./run-convert.sh) – Shell script to convert raw data into RDF format
- [`README.md`](./README.md) – Project documentation
  
## 🛠️ zbMATH Knowledge Graph: Construction and Setup

### Prerequisites

- Python 3.12+  
- Python libraries: `rdflib`, `SPARQLWrapper`, and others (see requirements.txt)  
- Java 8 or higher (required only if you run Apache Jena libraries outside Docker)  
- Docker (for running RDF triple stores like Apache Jena Fuseki without manual Java setup)  
  - We use [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) as an example for its simplicity  
  - *Note:* Production SPARQL endpoints use Virtuoso for scalability  

### Data Harvesting

```bash
python harvest-by-id.py 
```

### RDF Construction

```bash
# Option 1: Run the Python script
python create-rdf.py data/subset-200.jsonl subset-200

# Option 2: Run the shell script for batch processing
run-convert.sh

```

### RDF Triple Store Setup

We use [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) as our RDF triple store example. Fuseki provides a lightweight SPARQL server to host and query your knowledge graph. The example setup is provided in [`front/`](./front). 

```bash
docker compose up -d
```

This command runs Fuseki on port 3030 with the initial data uploaded via [`fuseki-entrypoint.sh`](front/fuseki-entrypoint.sh). )

## 🛠️ Historically-Grounded Retrieval Implementation

Run the following scripts to perform the respective retrieval tasks:

- **(1) Precursor Retrieval**  
  Identify overlooked foundational works beyond citation metrics.  
  ```bash
  python precursor-retrieval.py
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

### 📜 License

All content generated by zbMATH Open KG are distributed under [CC-BY-SA 4.0.](https://creativecommons.org/licenses/by-sa/4.0/)

📧 Contact: author@anonymous.org
