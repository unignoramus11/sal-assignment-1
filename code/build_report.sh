#!/usr/bin/env bash
# Builds the report PDF into the project root.
set -e
cd "$(dirname "$0")/.."
pandoc report/report.md \
  -o 2023111021_A1_report.pdf \
  --pdf-engine=xelatex \
  --resource-path=.:report \
  --metadata author="Mohit Singh (2023111021)"
echo "wrote 2023111021_A1_report.pdf"
