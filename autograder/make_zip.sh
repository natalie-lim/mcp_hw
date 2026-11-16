#!/usr/bin/env bash
# Build hw3-autograder.zip for Gradescope. Run from anywhere:
#     bash autograder/make_zip.sh
# The zip holds the test harness at the top level and the provided starter
# files (everything mcp_server.py imports) under provided/.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT

cp "$HERE"/{gs_shim.py,tests_hw3.py,run_tests.py,setup.sh,run_autograder} "$BUILD/"
mkdir -p "$BUILD/provided/data"
cp "$ROOT"/{embeddings.py,external_tool.py,ingest.py,llm.py,retriever.py} "$BUILD/provided/"
cp -R "$ROOT/data/corpus" "$BUILD/provided/data/"

rm -f "$HERE/hw3-autograder.zip"
(cd "$BUILD" && zip -qr -X "$HERE/hw3-autograder.zip" . -x '*/__pycache__/*' '*.pyc' '.DS_Store')
echo "wrote $HERE/hw3-autograder.zip"
