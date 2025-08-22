#!/bin/bash

set -e

PROJECT_ID="${1:-your-gcp-project-id}"
DATASET_ID="chess_games"
TABLE_ID="games"
REGION="us-central1"

echo "🔧 Creating BigQuery chess database..."
echo "Project: $PROJECT_ID"
echo "Dataset: $DATASET_ID"
echo "Table: $TABLE_ID"

# Set project
gcloud config set project $PROJECT_ID

# Create schema file
cat > bigquery_schema.json << 'EOF'
[
  {"name": "id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "white_player", "type": "STRING", "mode": "NULLABLE"},
  {"name": "black_player", "type": "STRING", "mode": "NULLABLE"},
  {"name": "event", "type": "STRING", "mode": "NULLABLE"},
  {"name": "site", "type": "STRING", "mode": "NULLABLE"},
  {"name": "date", "type": "DATE", "mode": "NULLABLE"},
  {"name": "round", "type": "STRING", "mode": "NULLABLE"},
  {"name": "result", "type": "STRING", "mode": "NULLABLE"},
  {"name": "eco", "type": "STRING", "mode": "NULLABLE"},
  {"name": "white_elo", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "black_elo", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "time_control", "type": "STRING", "mode": "NULLABLE"},
  {"name": "ply_count", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "pgn_text", "type": "STRING", "mode": "NULLABLE"},
  {"name": "commentary_stats", "type": "JSON", "mode": "NULLABLE"},
  {"name": "source_title", "type": "STRING", "mode": "NULLABLE"},
  {"name": "event_date", "type": "DATE", "mode": "NULLABLE"}
]
EOF

# Create dataset
bq mk --dataset --location=$REGION $PROJECT_ID:$DATASET_ID || echo "Dataset may already exist"

# Drop table if exists, then create
bq rm -f $PROJECT_ID:$DATASET_ID.$TABLE_ID || echo "Table didn't exist"
bq mk --table $PROJECT_ID:$DATASET_ID.$TABLE_ID bigquery_schema.json

echo "✅ BigQuery database created!"
echo "Ready to load data with pgn_to_bigquery.py"
