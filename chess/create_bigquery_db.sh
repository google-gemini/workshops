#!/bin/bash
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
