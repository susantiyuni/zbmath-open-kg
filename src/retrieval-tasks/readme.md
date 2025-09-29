## 🛠️ Historically-Grounded Retrieval

(1) Install the prerequisite libraries:

```bash
pip install -r requirements.txt
```

(2) Configure the SPARQL endpoint url in the script to match your KG's SPARQL endpoint.

```
# --- CONFIGURATION ---
endpoint_url = "http://localhost:8890/sparql"  # change into your SPARQL endpoint
```

(3) Run the following scripts to perform the respective retrieval tasks:

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

