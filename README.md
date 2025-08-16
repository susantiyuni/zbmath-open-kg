# zbMATH Open Knowledge Graph

A domain-specific knowledge graph derived from **zbMATH Open**, the world’s most comprehensive and historically rich mathematical database, covering scholarly work from 1868 to the present.

Enriched with manually curated expert reviews, disambiguated author profiles, and a fine-grained Mathematics Subject Classification (MSC) system, zbMATH Open provides a uniquely structured foundation for tracing the evolution of mathematical thought over more than 150 years.

## 📌 Key Features

- 🧠 **RDF-Based Knowledge Representation**  
  All entities and relationships are modeled as RDF triples, supporting semantic interoperability and Linked Open Data standards.

- 🔍 **SPARQL Endpoint**  
  Query the knowledge graph using SPARQL to retrieve complex and semantically rich information.

- 📚 **Curated Mathematical Metadata**  
  Includes publications, authors, expert-curated reviews, keywords, MSC classifications, and citation networks.

- 🔄 **Linked Data Integration**  
  Cross-referenced with external datasets (e.g., ORCID, Wikidata) to enhance entity resolution and connectivity.

## 📊 Statistics

- **Publications**: 4.5M+
- **Authors**: 1.2M+
- **Reviews**: 3.8M+
- **Subject Classifications (MSC)**: 5,000+
- **Triples**: 80M+

## 🏗️ Knowledge Graph Construction

### 🔧 Prerequisites

Ensure the following are installed:

- Python 3.8+
- Java 8+ (for RDF libraries Apache Jena)
- [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) or another SPARQL endpoint
- `pip` for Python dependency management

### 🛠️ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/zbmath-open-knowledge-graph.git
cd zbmath-open-knowledge-graph
pip install -r requirements.txt
