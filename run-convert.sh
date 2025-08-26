#!/bin/bash
#automate RDF building for all jsonl files in input directory
#e.g.,: python create-rdf.py out/out-1.jsonl out-1 --> results are saved in out-nt/out-1.nt and out-ttl/out-1.ttl

INPUT_DIR="out"
OUTPUT_DIR_1="out-ttl"
OUTPUT_DIR_2="out-nt"

mkdir -p "$OUTPUT_DIR_1"
mkdir -p "$OUTPUT_DIR_2"

for input_file in "$INPUT_DIR"/*.jsonl; do
    filename=$(basename "$input_file")
    base="${filename%.*}"  # Remove .jsonl extension
    output_prefix="${base}"

    echo "Processing $input_file -> $output_prefix"

    python src/create-rdf.py "$input_file" "$output_prefix"
done
