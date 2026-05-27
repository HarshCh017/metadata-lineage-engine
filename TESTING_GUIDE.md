# TESTING_GUIDE.md

# Enterprise Metadata Lineage Engine
# Complete Testing & Validation Guide

---

# OVERVIEW

This guide explains how to:

1. Setup the environment
2. Configure Neo4j
3. Run the QlikView parser
4. Load lineage into Neo4j
5. Validate parser output
6. Run automated tests
7. Run coverage reports
8. Test FastAPI APIs
9. Visualize lineage graphs
10. Validate enterprise lineage scenarios

This document is intended for:
- developers
- evaluators
- recruiters
- contributors
- testers

---

# SYSTEM REQUIREMENTS

| Component | Recommended |
|---|---|
| OS | Windows 10/11 |
| Python | 3.11.x |
| Neo4j | 5.x |
| RAM | 8 GB+ |

---

# IMPORTANT

Recommended Python version:

```text
Python 3.11.x
```

Avoid:
```text
Python 3.12+
```

because some parsing libraries may fail.

---

# STEP 1 — CLONE REPOSITORY

```powershell
git clone https://github.com/HarshCh017/metadata-lineage-engine.git
```

---

# STEP 2 — OPEN PROJECT

```powershell
cd metadata-lineage-engine
```

---

# STEP 3 — CREATE VIRTUAL ENVIRONMENT

```powershell
python -m venv .venv
```

---

# STEP 4 — ACTIVATE VIRTUAL ENVIRONMENT

```powershell
.\.venv\Scripts\Activate
```

Expected terminal:

```text
(.venv)
```

---

# STEP 5 — INSTALL DEPENDENCIES

```powershell
pip install -r requirements.txt
```

---

# STEP 6 — INSTALL & START NEO4J

Download:

https://neo4j.com/download/

Start Neo4j Desktop.

Default values:

| Setting | Value |
|---|---|
| Bolt URL | bolt://localhost:7687 |
| Browser | http://localhost:7474 |

---

# STEP 7 — CREATE `.env`

Create file:

```text
.env
```

Add:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

Replace password if needed.

---

# STEP 8 — VERIFY ENTERPRISE TEST FILE EXISTS

Check:

```text
data/input/qlikview/
```

Verify:

```text
99_enterprise_lineage_test.qvs
```

exists.

---

# STEP 9 — CLEAR NEO4J DATABASE

Open Neo4j Browser:

```text
http://localhost:7474
```

Run:

```cypher
MATCH (n)
DETACH DELETE n
```

---

# STEP 10 — VALIDATE PARSER

Run:

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); print('LOAD COUNT:', len(app.loads)); print('JOINS:', len(app.joins)); print('FIELDS:', len(app.fields))"
```

---

# EXPECTED OUTPUT

Example:

```text
LOAD COUNT: 11
JOINS: 4
FIELDS: 15
```

This confirms:
- parser is functioning
- joins are detected
- fields are extracted

---

# STEP 11 — LOAD GRAPH INTO NEO4J

Run:

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; from lineage_platform.neo4j.graph_writer import GraphWriter; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); writer = GraphWriter(); writer.write_app(app); print('GRAPH WRITTEN SUCCESSFULLY')"
```

---

# EXPECTED OUTPUT

```text
GRAPH WRITTEN SUCCESSFULLY
```

---

# STEP 12 — VERIFY GRAPH EXISTS

Run in Neo4j:

```cypher
MATCH (n)
RETURN count(n)
```

Expected:

```text
100+
```

---

# STEP 13 — VISUALIZE GRAPH

Run:

```cypher
MATCH (a)-[r]->(b)
RETURN a,r,b
LIMIT 200
```

Expected:
- tables
- attributes
- lineage relationships
- joins
- derived fields

---

# STEP 14 — TEST ATTRIBUTE LINEAGE

Run:

```cypher
MATCH (a:Attribute)-[:DERIVED_FROM]->(b)
RETURN a.name, b.name
ORDER BY a.name
```

Expected lineage examples:

| Derived Field | Source Field |
|---|---|
| AmountWithTax | Amount |
| CustomerStatus | Status |
| OrderCount | OrderID |
| AvgBasketValue | Amount |
| ProductHierarchy | Category |

---

# STEP 15 — TEST MULTI-HOP LINEAGE

Run:

```cypher
MATCH path = (a:Attribute)-[:DERIVED_FROM*]->(b)
RETURN path
LIMIT 50
```

Expected chains:

```text
LifetimeRevenue
    ↓
TotalAmount
    ↓
Amount
```

and:

```text
AvgBasketValue
    ↓
AverageAmount
    ↓
Amount
```

---

# STEP 16 — TEST JOIN LINEAGE

Run:

```cypher
MATCH (a:QlikTable)-[r:JOINED_WITH]->(b)
RETURN a.name, r.type, b.name
```

Expected:
- LEFT JOIN
- INNER JOIN
- RESIDENT joins

---

# STEP 17 — START FASTAPI SERVER

Run:

```powershell
python -m uvicorn lineage_platform.api.app:app --reload
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# STEP 18 — OPEN SWAGGER DOCS

Open:

```text
http://127.0.0.1:8000/docs
```

Expected:
- interactive APIs
- health endpoint
- metadata endpoints

---

# STEP 19 — TEST HEALTH API

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

# STEP 20 — GET NODE IDS

Run in Neo4j:

```cypher
MATCH (n)
WHERE n.id IS NOT NULL
RETURN n.name, n.id
LIMIT 10
```

Copy one UUID.

Example:

```text
9f364159-0b9f-4404-ab42-8415b5e68c47
```

---

# STEP 21 — TEST NODE METADATA API

Open:

```text
http://127.0.0.1:8000/api/v1/node/<UUID>
```

Example:

```text
http://127.0.0.1:8000/api/v1/node/9f364159-0b9f-4404-ab42-8415b5e68c47
```

Expected JSON:

```json
{
  "labels": ["Attribute"],
  "properties": {
    "name": "OrderCount",
    "formula": "COUNT(OrderID)",
    "datatype": "decimal",
    "is_calculated": true
  },
  "connections": [
    {
      "relationship": "DERIVED_FROM",
      "connected_node": "OrderID"
    }
  ]
}
```

---

# STEP 22 — RUN AUTOMATED TESTS

Run:

```powershell
pytest
```

Expected:

```text
6 passed
```

or higher.

---

# STEP 23 — RUN TEST COVERAGE

Run:

```powershell
pytest --cov=lineage_platform --cov-report=term-missing
```

Expected:

```text
70%+ coverage
```

Core parser modules should show:
- 90%+ parser coverage
- 90%+ lineage extraction coverage

---

# STEP 24 — GENERATE HTML COVERAGE REPORT

Run:

```powershell
pytest --cov=lineage_platform --cov-report=html
```

Open:

```powershell
start htmlcov\index.html
```

Expected:
- detailed file coverage
- missing lines
- parser coverage visualization

---

# STEP 25 — TEST DOCKER BUILD

Build image:

```powershell
docker build -t metadata-lineage-engine .
```

Run container:

```powershell
docker run -p 8000:8000 metadata-lineage-engine
```

---

# STEP 26 — VERIFY CI/CD

Open GitHub Actions:

```text
https://github.com/HarshCh017/metadata-lineage-engine/actions
```

Expected:
- automated test execution
- successful workflow runs

---

# RECOMMENDED NEO4J VISUALIZATION

Run:

```cypher
MATCH path = (n)-[*1..4]-(m)
RETURN path
LIMIT 200
```

This gives the best graph visualization.

---

# RECOMMENDED NEO4J STYLING

Configure:

| Node Type | Caption |
|---|---|
| Attribute | name |
| QlikTable | name |

Recommended colors:

| Node | Color |
|---|---|
| Attribute | Blue |
| QlikTable | Green |
| Table | Orange |

---

# EXPECTED SUCCESS CRITERIA

| Capability | Expected |
|---|---|
| LOAD parsing | ✅ |
| JOIN parsing | ✅ |
| SQL lineage | ✅ |
| Attribute lineage | ✅ |
| Multi-hop lineage | ✅ |
| Neo4j graph | ✅ |
| Metadata APIs | ✅ |
| Swagger docs | ✅ |
| Automated tests | ✅ |
| Coverage reports | ✅ |
| CI/CD | ✅ |

---

# COMMON ERRORS

---

# Error: ModuleNotFoundError

Cause:
Wrong project directory.

Fix:

```powershell
cd metadata-lineage-engine
```

---

# Error: No module named neo4j

Fix:

```powershell
pip install neo4j
```

---

# Error: pytest command not found

Fix:

```powershell
pip install pytest pytest-cov
```

---

# Error: app not found

Verify:

```text
lineage_platform/api/app.py
```

contains:

```python
app = FastAPI(...)
```

---

# Error: Node not found

Cause:
Using old UUID after graph reload.

Fix:
Fetch fresh node IDs from Neo4j.

---

# Error: LOAD COUNT = 0

Cause:
Broken parser or missing QVS file.

Fix:
Verify:

```text
99_enterprise_lineage_test.qvs
```

exists.

---

# TECHNOLOGY STACK

| Component | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| Graph Database | Neo4j |
| SQL Parsing | sqlglot |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Visualization | Neo4j Browser |

---

# PROJECT STATUS

Current maturity:

```text
Enterprise-style engineering MVP
```

Includes:
- parser engine
- graph lineage
- automated testing
- metadata APIs
- CI/CD
- Docker support

---

# END