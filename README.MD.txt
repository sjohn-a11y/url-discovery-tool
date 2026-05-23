# Harvester QA Tool

This tool helps process Excel files and generate Action Required summaries.

## Features
- Upload Excel
- Filter by Assignee
- Select Entity ID
- Transpose source data
- Auto detect issues (404, 500, duplicates)
- Download report

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py