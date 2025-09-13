#!/usr/bin/env bash
set -euo pipefail

# Prepare any additional data required by the pipeline.
# Notes from instructions:
# - Primary PDB is already present in each variant folder; no download needed.
# - If any retrieval is needed, store outputs under data_output/ in the variant folder.

VARIANT_DIR=${1:?"Usage: prepare_data.sh <variant_dir>"}
DATA_OUT_DIR="$VARIANT_DIR/data_output"
mkdir -p "$DATA_OUT_DIR"

# Placeholder for potential retrieval/derivation steps.
# For now, we just ensure the output directory exists.
# Example of retrievable artifact (commented):
# curl -sSL "https://example.org/aux-data" -o "$DATA_OUT_DIR/aux.txt"

echo "Data prepared at: $DATA_OUT_DIR"
