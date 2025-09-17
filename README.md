# zbMATH Open Knowledge Graph

We construct a large-scale, historically deep knowledge graph derived from [**zbMATH Open**](https://zbmath.org/), the world’s most comprehensive and historically rich mathematical database, covering scholarly work from 1763 to the present.

The resulting **zbMATH Knowledge Graph (KG)**, fully compliant with RDF and Semantic Web standards, interconnects publication metadata while leveraging the unique features of zbMATH:

- Expert-curated reviews
- High-quality author disambiguation
- Expert-assigned keywords and *Mathematics Subject Classification* (MSC), a fine-grained and historically stable ontology of mathematical subjects

This combination provides a rich semantic foundation for capturing the long-term evolution of mathematical knowledge, enabling advanced retrieval and reasoning beyond conventional citation-based bibliometric methods.

Through several **case studies**, we demonstrate the ability of the zbMATH KG to:

- Uncover **overlooked precursors** beyond traditional citation analysis
- Reveal **conceptual ancestry across fields**
- Trace **concept revivals** in new contexts
- Map **author–reviewer intellectual lineage**, illustrating how ideas propagate via scholarly interactions

These **historically-grounded retrieval** methods expose intellectual dynamics that conventional citation-based systems in scholarly domains often fail to capture. 

---

## 📊 Key Statistics
- **Triples**: 159M+
- **Distinct Entities**: 36M+
- **Publications**: 4M+
- **Authors/Reviewers**: 1M+
- **Reviews**: 3M+
- **Subject Classifications (MSC)**: 6,500+
- **Keywords**: 3M+
- **Software**: 30k+ ... (and more)

## 📌 Key Features

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
  
## 🛠️ Knowledge Graph Construction and Setup

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

### 📜 License

All content generated by zbMATH Open KG are distributed under [CC-BY-SA 4.0.](https://creativecommons.org/licenses/by-sa/4.0/)

📧 Contact: author@anonymous.org
