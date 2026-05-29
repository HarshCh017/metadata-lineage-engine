# Enterprise Testing & Validation Guide

The Metadata Lineage Engine relies on a rigorous test pyramid extending beyond basic unit tests to include fuzzing, regression, semantic validations, and high-density stress testing.

## 1. Running the Enterprise Test Suite
You can execute all governance validations, benchmarks, and temporal latency tests using the entrypoint script:
```bash
python run_enterprise_test.py
```
This runs four phases:
1. **Core Validation**: Executes `pytest tests/` (Semantic validations, regressions, unit tests).
2. **Stress Validation**: Executes `pytest benchmarks/test_graph_density.py` (simulates 10 Million relationships to test governance overhead limits).
3. **Temporal Benchmarks**: Executes `pytest benchmarks/test_temporal_benchmark.py` (verifies historical snapshot queries perform under SLA constraints).
4. **Federated Governance Benchmarks**: Executes `pytest benchmarks/test_federated_scale.py` (verifies priority-tiered WorkloadManager behavior and synchronous Policy Evaluation overhead for 100k+ payloads).

## 2. Test Categories

### Fuzz Testing (`tests/fuzzing/`)
Tests the `ParserRecoveryEngine`. The fuzz suite injects thousands of malformed or randomized syntax variations into the parser to guarantee that:
- The system never crashes with uncaught exceptions.
- It degrades cleanly into `REGEX_FALLBACK`, `AST_RECOVERY`, etc.
- Multi-dimensional confidence scores correctly reflect the degradation.

### Corpus Regression (`tests/corpus/`)
Validates that the semantic ontology (JSON structure) extracted from Gold Standard scripts NEVER drifts. 
- Prevents breaking downstream consumers (e.g., OpenLineage schemas).

### Graph Density Stress Tests (`benchmarks/test_graph_density.py`)
Validates the `QueryGovernanceEngine` boundaries:
- Enforces `MAX_TRAVERSAL_DEPTH` (default 100).
- Prevents massive fanouts via `MAX_NODE_FANOUT_BUDGET`.
- Ensures that query interception overhead adds `<100ms` latency.

### Semantic Validations (`lineage_platform/validation/semantic_validator.py`)
Ensures that the output of the parser represents mathematically valid lineage:
- No orphaned active fields inside derivations.
- Non-deterministic mappings (e.g. `SELECT *` from unknown sources) correctly downgrade confidence.

---

# Step-by-Step Practical Validation Guide

Follow these steps to fully verify the Metadata Lineage Engine locally in your VS Code environment.

## 1. Environment Setup

First, ensure your virtual environment is activated and you have all the updated dependencies installed:

```powershell
# 1. Activate your virtual environment (if not already active)
.\.venv\Scripts\activate

# 2. Install all requirements
pip install -r requirements.txt
```

## 2. Start the Graph Database

The engine requires Neo4j to store the extracted lineage graph.

```powershell
# Start Neo4j in the background via Docker
docker-compose up -d neo4j
```

Wait a few seconds for the database to fully initialize.

## 3. Manual API Verification

Once the tests pass, start the live API server:

```powershell
python -m uvicorn lineage_platform.api.app:app --reload
```

When you see `Application startup complete`, follow these steps to manually push a payload:

1. Open your browser and go to [http://localhost:8000/docs](http://localhost:8000/docs).
2. Expand the **Lineage** section and click on `POST /api/v1/parse`.
3. Click **"Try it out"**.
4. In the request body, use the absolute path to our enterprise test QVS file (adjust the `C:\` path if your desktop path differs):
   ```json
   {
     "script_path": "C:\\Users\\HarshChauhan\\Desktop\\metadata-lineage-engine\\data\\input\\qlikview\\99_enterprise_lineage_test.qvs",
     "overwrite": true
   }
   ```
5. Click **Execute**.
6. You should immediately see a `200 OK` response with a JSON body indicating `"status": "success"`.

## 4. Verify the Graph (Neo4j)

Finally, verify the nodes and edges were properly written to Neo4j.

1. Open [http://localhost:7474](http://localhost:7474) in your browser.
2. Log in with Username: `neo4j` and Password: `password` (if prompted).
3. Ensure the active database at the top left is set to **`neo4j`** (not `system`).
4. Try running the following **Cypher queries** in the top command bar to explore different aspects of your metadata lineage:

### Basic Graph Overview
See everything (up to 100 nodes) to verify the data was inserted:
```cypher
MATCH (n) RETURN n LIMIT 100
```

### View Only Tables and Their Connections
See all tables and how data flows between them. (Note: Qlik tables are labeled `QlikTable`):
```cypher
MATCH p=(:QlikTable)-[r:DERIVES_FROM_TABLE]->(:QlikTable)
RETURN p LIMIT 50
```

### Trace Full Upstream Lineage for a Dashboard
Find the specific dashboard dataset, and trace all the way back to the source Qlik tables:
```cypher
MATCH p=(d:Dataset {name: 'DashboardDataset'})-[*1..5]->(source:QlikTable)
RETURN p
```

### View Tables and Their Extracted Fields
Since field-level lineage is not mapped in this phase, use this to see all fields attached to their tables:
```cypher
MATCH p=(t:QlikTable)-[:HAS_FIELD]->(a:Attribute)
RETURN p LIMIT 50
```

### View How Tables Join Together
See the explicit JOIN relationships extracted by the parser:
```cypher
MATCH p=(:QlikTable)-[r:JOINS_WITH]->(:QlikTable)
RETURN p
```

### Count Everything by Node Type
Get a statistical breakdown of everything the parser extracted:
```cypher
MATCH (n)
RETURN labels(n) as Type, count(n) as Count
ORDER BY Count DESC
```

You will see a beautiful graph visualization of the tables, fields, processes, and their lineage relationships!