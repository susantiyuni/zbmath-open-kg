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
