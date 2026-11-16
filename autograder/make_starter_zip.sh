#!/usr/bin/env bash
# Build hw3-starter.zip, the copy students download. Run from anywhere:
#     bash autograder/make_starter_zip.sh
# Takes only git-tracked files (so .env, caches, and index.json can never be
# included) and leaves out the staff-only solution/ and autograder/ folders.
# Files are copied from the working tree, so uncommitted edits are included.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT

mkdir "$BUILD/hw3"
cd "$ROOT"
git ls-files | grep -v -E '^(solution|autograder)/' | while IFS= read -r f; do
    mkdir -p "$BUILD/hw3/$(dirname "$f")"
    cp "$f" "$BUILD/hw3/$f"
done

rm -f "$HERE/hw3-starter.zip"
(cd "$BUILD" && zip -qr -X "$HERE/hw3-starter.zip" hw3)
echo "wrote $HERE/hw3-starter.zip"
