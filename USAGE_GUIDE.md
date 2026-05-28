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
You can interact with the graph natively via Python:
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

## Step 6: Connect Claude via MCP
You can natively connect Claude Desktop to this lineage engine to ask natural language questions about your data ecosystem.

Edit your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "qlik-lineage": {
      "command": "python",
      "args": ["-m", "lineage_platform.mcp_server"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```
Restart Claude Desktop, and you can now ask: *"What tables feed into the Sales dashboard?"* or *"Show me the temporal lineage for CUSTOMER_DIM as of January 1st."*

## Step 7: Observability
Visit `http://localhost:8000/metrics` to scrape Prometheus telemetry.
Key metrics to monitor:
- `lineage_parse_failures_total`
- `lineage_fallback_rates_total`
- `lineage_parse_latency_seconds`

## Step 8: Validation & Benchmarks
To run the fuzzing validations to ensure parser correctness:
```bash
python -m pytest tests/fuzzing/ -v
```

To validate the semantic ontology against the gold standard corpus:
```bash
python -m pytest tests/corpus/ -v
```

To validate the system scale and temporal overhead on your hardware:
```bash
python benchmarks/run_benchmarks.py
```
This will execute the Incremental Refresh test, the Graph Write Batch test (simulating 1,000 tables / 50,000 columns), and the Temporal Overhead test.
