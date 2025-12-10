## zbMATH Open KG: RDF Triple Store Setup (Virtuoso)

This example demonstrates how to set up the zbMATH Open KG using [Virtuoso](https://virtuoso.openlinksw.com/) as the RDF triple store. 

### Requirements

- [Docker](https://www.docker.com/get-started) (includes Docker Compose)

### Running virtuoso

Make sure your RDF data is placed in the correct local directory. In the example below, files must be located in ```/local/toLoad```, 

and mounted inside the container as:

```yaml
- /local/toLoad:/opt/virtuoso-opensource/database/toLoad
```

Then, start Virtuoso by running:
```bash
docker compose up -d
```

Once the service is running, the SPARQL endpoint will be available at: `http://localhost:3030/dataset/sparql`

### Uploading Data (manual)
We provide a sample subset of the zbMATH Open KG data you can use here: [`data/subset-200.ttl`](./data/subset-200.ttl).

To load the data manually, first, enter the Virtuoso ISQL Shell

```
docker exec -it virtuoso isql 1111 dba dba
```

Then load a single RDF file:

```
ld_dir('/opt/virtuoso-opensource/database/toLoad', 'out-1.ttl', 'https://zbmath.org');
rdf_loader_run();
checkpoint;
```

Or load multiple files (all .ttl):

```
ld_dir('/opt/virtuoso-opensource/database/toLoad', '%.ttl', 'https://zbmath.org');
rdf_loader_run();
checkpoint;
```

Depending on file size, loading may take several minutes. 

### Checking Upload Progress

You can monitor whether RDF loading is working by observing changes in the database file size.

Open a shell inside the container:

```
docker exec -it virtuoso bash 
```

Check the size of the Virtuoso database:

```
ls -lh /opt/virtuoso-opensource/database/virtuoso.db
```

Run this command a few times; if the file size increases, data is still being loaded.

You can also verify by running queries directly against the SPARQL endpoint: `http://localhost:3030/dataset/sparql`

### Uploading Data (.bash script)

We prepare a .bash script [`load-data.sh`](./load-data.sh) to automate both the data upload and the progress checking. 
Make sure that the file is executable ```chmod +x load_data.sh```

This script:

- Copies your ```.ttl``` files into the Virtuoso ```toLoad``` directory
- Runs ```ld_dir``` + ```rdf_loader_run``` inside ISQL
- Prints database size repeatedly so you can monitor progress

### Other Settings

Additional configuration options for Virtuoso can be adjusted in the: ```virtuoso.ini```

This file allows you to modify settings such as

- Default SPARQL query shown in the endpoint UI
```
  DefaultQuery = SELECT (COUNT(*) AS ?count) FROM <https://zbmath.org> WHERE { ?s ?p ?o }
  ```
- Maximum SPARQL query execution time
```
MaxQueryExecutionTime = 10000	; in seconds
```
and other logging and performance options e.g., memory limits and buffer sizes, directory paths for database and RDF loading.
Edit the file as needed before starting the container, or rebuild/restart the service after making changes.
