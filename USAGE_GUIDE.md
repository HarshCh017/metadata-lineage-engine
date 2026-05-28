# Metadata Lineage Engine - Step by Step Usage Guide

## Prerequisites
- Python 3.11+
- Neo4j Database (or Docker for Neo4j)
- `pip install -r requirements.txt`

## Step 1: Start Neo4j Database
If you don't have a remote Neo4j instance, start a local one using Docker Compose:
```bash
docker-compose up -d neo4j
```
This will expose Neo4j on `localhost:7687` and `localhost:7474`.

## Step 2: Configure Environment
Copy `.env.example` to `.env` and configure your settings:
```bash
cp .env.example .env
```
Ensure `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` are correct.
For Graph Compaction, adjust `LINEAGE_RETENTION_DAYS` (default 90).

## Step 3: Run the API Server
Start the FastAPI application:
```bash
python -m uvicorn lineage_platform.api.app:app --reload --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/docs` to see the Swagger UI.

## Step 4: Parse a Script
You can submit a Qlik script for parsing via the `/parse` endpoint.
```bash
curl -X 'POST' \
  'http://localhost:8000/parse' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "script_path": "tests/data/sample_qvs.qvs",
  "overwrite": false
}'
```
*Note: If `overwrite: false`, submitting the exact same file twice will bypass the parser using Incremental Hash Detection.*

## Step 5: Querying Temporal Lineage
You can interact with the graph via the MCP server using Claude Desktop, or natively via Python:
```python
from lineage_platform.api.services.graph_service import GraphService
from lineage_platform.models.snapshot import SnapshotContext

svc = GraphService()

# Current Active Lineage
print(svc.get_table_lineage("db.schema.target_table"))

# Historical Lineage (Time Travel)
snapshot = SnapshotContext(as_of_timestamp="2024-01-01T00:00:00Z")
print(svc.get_table_lineage("db.schema.target_table", snapshot=snapshot))
```

## Step 6: Observability
Visit `http://localhost:8000/metrics` to scrape Prometheus telemetry.

## Step 7: Run Benchmarks (Optional)
To validate the system scale and temporal overhead on your hardware:
```bash
python benchmarks/run_benchmarks.py
```
This will run the Incremental Refresh test, the Graph Write Batch test, and the Temporal Overhead test.
