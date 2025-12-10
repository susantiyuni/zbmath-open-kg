#!/bin/bash
## make this file executable chmod +x load_data.sh

# ---------------------------------------------
# Config
# ---------------------------------------------
CONTAINER_NAME="virtuoso"
LOAD_DIR="/opt/virtuoso-opensource/database/toLoad"
LOCAL_DATA_DIR="./local/toLoad"        # local directory where your TTL files exist
GRAPH_URI="https://zbmath.org"

# ---------------------------------------------
# Step 1: Copy files into the container
# ---------------------------------------------
echo " Copying TTL files into Virtuoso container..."
docker cp $LOCAL_DATA_DIR/. $CONTAINER_NAME:$LOAD_DIR

echo "✔ Data copied."

# ---------------------------------------------
# Run ld_dir and rdf_loader_run
# ---------------------------------------------
echo "Starting RDF load..."
docker exec -i $CONTAINER_NAME isql 1111 dba dba <<EOF
ld_dir('$LOAD_DIR', '%.ttl', '$GRAPH_URI');
rdf_loader_run();
checkpoint;
EOF

echo "✔ RDF load triggered."

# ---------------------------------------------
# Monitor DB size for progress
# ---------------------------------------------
echo "Monitoring virtuoso.db size (Ctrl+C to stop)..."
echo "---------------------------------------------"

while true; do
    docker exec $CONTAINER_NAME bash -c "ls -lh /opt/virtuoso-opensource/database/virtuoso.db"
    sleep 5
done
