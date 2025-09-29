## zbMATH Open KG: RDF Triple Store Setup

### Requirements

- [Docker](https://www.docker.com/get-started) (includes Docker Compose)


This example demonstrates how to set up the zbMATH Open KG using [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) as the RDF triple store. Fuseki is a lightweight SPARQL server that allows you to host and query your knowledge graph easily.

We provide a sample subset of the zbMATH Open KG data you can use here: [`data/subset-200.ttl`](./data/subset-200.ttl).

Before running the example, ensure the initial data file is located in the same folder as the `docker-compose.yml` file. 
If not, update the volume mapping in `docker-compose.yml` accordingly:

```yaml
- ./subset-200.ttl:/data.ttl
```

Then, start the service by running:
```bash
docker compose up -d
```

This will launch Fuseki on port 3030 and load the initial data via [`fuseki-entrypoint.sh`](front/fuseki-entrypoint.sh).

Your SPARQL endpoint URL will be available at: `http://localhost:3030/dataset/sparql`
