#!/usr/bin/env bash
set -e

/jena-fuseki/fuseki-server --update --mem /dataset &
PID=$!

echo "Waiting for Fuseki to start..."
until curl -s http://localhost:3030 >/dev/null; do
    sleep 1
done
echo "Fuseki is up. Uploading data..."

curl -u admin:admin -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @/data.ttl \
  http://localhost:3030/dataset/data

echo "Data upload complete."

wait $PID
