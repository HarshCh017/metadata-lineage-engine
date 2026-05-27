# Enterprise Lineage Platform
# Step-by-Step Setup & Execution Guide
# Running: 99_enterprise_lineage_test.qvs

---

# OVERVIEW

This guide explains how to:

1. Install the project
2. Configure Python
3. Configure Neo4j
4. Install dependencies
5. Load the enterprise QVS test file
6. Build lineage graph
7. Run FastAPI APIs
8. Visualize lineage in Neo4j

This guide assumes:
- fresh machine
- no prior setup
- Windows system
- beginner user

---

# STEP 1 — INSTALL PYTHON

## Recommended Version

Install:

```text
Python 3.11.x
```

DO NOT use:
```text
Python 3.12+
```

because some parsing libraries may fail.

---

# DOWNLOAD PYTHON

Download from:

https://www.python.org/downloads/release/python-3119/

---

# IMPORTANT DURING INSTALLATION

CHECK:

```text
Add Python to PATH
```

before clicking Install.

---

# VERIFY INSTALLATION

Open PowerShell:

Run:

```powershell
python --version
```

Expected:

```text
Python 3.11.x
```

---

# STEP 2 — INSTALL NEO4J

Download Neo4j Desktop:

https://neo4j.com/download/

Install it.

---

# STEP 3 — START NEO4J

Open Neo4j Desktop.

Create a local database.

Start database.

Default settings:

| Setting | Value |
|---|---|
| Bolt URL | bolt://localhost:7687 |
| Browser URL | http://localhost:7474 |

---

# STEP 4 — OPEN PROJECT

Extract/download project files.

Open PowerShell.

Navigate to project folder:

Example:

```powershell
cd "C:\Users\YourName\Desktop\lineage-platform"
```

---

# STEP 5 — CREATE VIRTUAL ENVIRONMENT

Run:

```powershell
python -m venv .venv
```

---

# STEP 6 — ACTIVATE VIRTUAL ENVIRONMENT

Run:

```powershell
.\.venv\Scripts\Activate
```

Expected:

```text
(.venv)
```

appears in terminal.

---

# STEP 7 — INSTALL REQUIREMENTS

Run:

```powershell
pip install -r requirements.txt
```

Wait until installation completes.

---

# STEP 8 — CREATE .ENV FILE

Inside project root create file:

```text
.env
```

Add:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

Replace password if your Neo4j password differs.

---

# STEP 9 — VERIFY PROJECT STRUCTURE

You should have:

```text
lineage-platform/
│
├── lineage_platform/
├── data/
├── requirements.txt
├── README.md
└── .env
```

---

# STEP 10 — VERIFY TEST FILE EXISTS

Check:

```text
data/input/qlikview/
```

You should see:

```text
99_enterprise_lineage_test.qvs
```

---

# STEP 11 — CLEAR NEO4J DATABASE

Open Neo4j Browser:

```text
http://localhost:7474
```

Login.

Run:

```cypher
MATCH (n)
DETACH DELETE n
```

Expected:

```text
No changes, no records
```

---

# STEP 12 — TEST PARSER

Go back to PowerShell.

Run:

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); print('LOAD COUNT:', len(app.loads)); print('JOINS:', len(app.joins)); print('FIELDS:', len(app.fields))"
```

---

# EXPECTED OUTPUT

Something like:

```text
LOAD COUNT: 11
JOINS: 4
FIELDS: 15
```

This confirms parser is working.

---

# STEP 13 — LOAD GRAPH INTO NEO4J

Run:

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; from lineage_platform.neo4j.graph_writer import GraphWriter; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); writer = GraphWriter(); writer.write_app(app); print('GRAPH WRITTEN SUCCESSFULLY')"
```

---

# EXPECTED OUTPUT

```text
GRAPH WRITTEN SUCCESSFULLY
```

WITHOUT errors.

---

# STEP 14 — VERIFY GRAPH EXISTS

Open Neo4j Browser.

Run:

```cypher
MATCH (n)
RETURN count(n)
```

Expected:

```text
100+
```

---

# STEP 15 — VIEW GRAPH

Run:

```cypher
MATCH (a)-[r]->(b)
RETURN a,r,b
LIMIT 200
```

You should now visually see:
- tables
- joins
- attributes
- lineage relationships

---

# STEP 16 — TEST ATTRIBUTE LINEAGE

Run:

```cypher
MATCH (a:Attribute)-[:DERIVED_FROM]->(b)
RETURN a.name, b.name
ORDER BY a.name
```

Expected lineage:

| Derived Field | Source Field |
|---|---|
| AmountWithTax | Amount |
| CustomerStatus | Status |
| OrderCount | OrderID |
| ProductHierarchy | Category |
| ProductHierarchy | SubCategory |

---

# STEP 17 — TEST MULTI-HOP LINEAGE

Run:

```cypher
MATCH path = (a:Attribute)-[:DERIVED_FROM*]->(b)
RETURN path
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

# STEP 18 — START FASTAPI SERVER

Go back to PowerShell.

Run:

```powershell
python -m uvicorn lineage_platform.api.app:app --reload
```

Expected:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

# STEP 19 — OPEN SWAGGER DOCS

Open browser:

```text
http://127.0.0.1:8000/docs
```

You should see:
- Metadata APIs
- Lineage APIs
- Health APIs

---

# STEP 20 — TEST NODE METADATA API

Get node IDs from Neo4j:

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

# STEP 21 — OPEN METADATA API

Open:

```text
http://127.0.0.1:8000/api/v1/node/<UUID>
```

Example:

```text
http://127.0.0.1:8000/api/v1/node/9f364159-0b9f-4404-ab42-8415b5e68c47
```

---

# EXPECTED JSON RESPONSE

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

# STEP 22 — BEST GRAPH VISUALIZATION

Run:

```cypher
MATCH path = (n)-[*1..4]-(m)
RETURN path
LIMIT 200
```

This gives the best graph visualization.

---

# STEP 23 — OPTIONAL NEO4J STYLING

In Neo4j Browser:

1. Click settings/gear icon
2. Configure captions:

| Label | Caption |
|---|---|
| Attribute | name |
| QlikTable | name |

3. Configure colors:

| Node Type | Color |
|---|---|
| Attribute | Blue |
| QlikTable | Green |
| Table | Orange |

---

# SUCCESS CRITERIA

If successful you should have:

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

---

# COMMON ERRORS

---

# Error: ModuleNotFoundError

Cause:
Wrong directory.

Fix:

```powershell
cd lineage-platform
```

---

# Error: No module named neo4j

Fix:

```powershell
pip install neo4j
```

---

# Error: app not found

Fix:
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
Old UUID used after graph reload.

Fix:
Query fresh IDs from Neo4j.

---

# Error: LOAD COUNT = 0

Cause:
Broken parser or missing test file.

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
| Backend API | FastAPI |
| Graph Database | Neo4j |
| Parsing | Python Regex + Line Parser |
| SQL Parsing | sqlglot |
| Metadata Graph | Neo4j |
| Visualization | Neo4j Browser |

---

# FUTURE ENHANCEMENTS

- Tableau lineage
- Ab Initio parsing
- Impact analysis
- Search APIs
- Business glossary
- Deterministic IDs
- ANTLR parser engine
- Full AST parsing

---

# END