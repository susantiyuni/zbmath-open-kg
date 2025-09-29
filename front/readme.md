### zbMATH KG: RDF Triple Store Setup

This is an example for setting zbMATH Open KG using [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) as our RDF triple store example. Fuseki provides a lightweight SPARQL server to host and query your knowledge graph.  

```bash
docker compose up -d
```

This command runs Fuseki on port 3030 with the initial data uploaded via [`fuseki-entrypoint.sh`](front/fuseki-entrypoint.sh). )
