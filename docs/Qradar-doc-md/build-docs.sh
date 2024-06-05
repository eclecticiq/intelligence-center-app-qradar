#!/usr/bin/env bash

if [[ ! $(command -v pandoc) ]]; then
  echo Need pandoc to build documentation.
  exit 1
fi

OUTPUT="../USER-MANUAL.pdf"

echo "Writing PDF to ${OUTPUT}"


pandoc -f markdown -t pdf \
  -o "${OUTPUT}" \
  --pdf-engine=xelatex \
  --highlight-style=pygments \
  -V colorlinks \
  -V linkcolor='[HTML]{0000DD}' \
  USER-MANUAL.md 

