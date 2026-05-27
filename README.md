# Enterprise Lineage Platform

Enterprise metadata lineage platform for parsing QlikView scripts and building attribute-level lineage graphs in Neo4j.

---

# Features

## Current Capabilities

### QlikView Parsing
- SQL LOAD parsing
- RESIDENT LOAD parsing
- JOIN parsing
- CONCATENATE parsing
- GROUP BY parsing
- Synthetic field extraction
- Aggregation lineage
- ApplyMap parsing
- IF condition lineage

### Metadata Lineage
- Table-level lineage
- Column-level lineage
- Attribute-level lineage
- Multi-hop lineage
- Derived field tracing
- Join relationships
- Source-to-target mapping

### Neo4j Graph
- Graph-based lineage storage
- Relationship traversal
- Interactive graph visualization
- Metadata enrichment
- UUID node identification

### FastAPI Backend
- Metadata APIs
- Node detail APIs
- Health APIs
- Swagger documentation

---

# Architecture

```text
QlikView Script (.qvs)
            ↓
        QVS Parser
            ↓
    Metadata Models
            ↓
       Neo4j Writer
            ↓
       Neo4j Graph
            ↓
      FastAPI APIs
            ↓
     Metadata Explorer
```

---

# Project Structure

```text
lineage-platform/
│
├── lineage_platform/
│   │
│   ├── api/
│   │   ├── app.py
│   │   └── routes/
│   │       ├── lineage_routes.py
│   │       └── node_details.py
│   │
│   ├── batch/
│   │   └── file_discovery.py
│   │
│   ├── cli/
│   │   └── main.py
│   │
│   ├── models/
│   │   └── qlik_models.py
│   │
│   ├── neo4j/
│   │   └── graph_writer.py
│   │
│   ├── parsers/
│   │   └── qlikview/
│   │       ├── qvs_parser.py
│   │       ├── field_parser.py
│   │       ├── join_parser.py
│   │       ├── synthetic_field_parser.py
│   │       ├── sql_parser.py
│   │       └── connection_parser.py
│   │
│   └── utils/
│
├── data/
│   └── input/
│       └── qlikview/
│
├── requirements.txt
├── README.md
└── .env
```

---

# Requirements

## Recommended Python Version

```text
Python 3.11.x
```

Avoid:
```text
Python 3.12+
```

---

# Installation

## 1. Clone Project

```powershell
git clone <repo-url>
cd lineage-platform
```

---

## 2. Create Virtual Environment

```powershell
python -m venv .venv
```

---

## 3. Activate Virtual Environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate
```

---

## 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# Neo4j Setup

## Install Neo4j

Download:

https://neo4j.com/download/

---

## Start Neo4j

Default:
- Bolt URL: `bolt://localhost:7687`
- Browser: `http://localhost:7474`

---

## Create `.env`

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

---

# Running the Parser

---

# Parse Single QVS File

Example:

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); print(app)"
```

---

# Validate Parsing

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); print('LOAD COUNT:', len(app.loads)); print('JOINS:', len(app.joins)); print('FIELDS:', len(app.fields))"
```

Expected:
- multiple LOAD blocks
- multiple joins
- synthetic fields

---

# Load Data into Neo4j

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; from lineage_platform.neo4j.graph_writer import GraphWriter; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); writer = GraphWriter(); writer.write_app(app); print('GRAPH WRITTEN SUCCESSFULLY')"
```

---

# Neo4j Queries

---

# View Entire Graph

```cypher
MATCH (n)
RETURN n
LIMIT 100
```

---

# View Relationships

```cypher
MATCH (a)-[r]->(b)
RETURN a,r,b
LIMIT 200
```

---

# View Table Lineage

```cypher
MATCH (a:QlikTable)-[:READS_FROM]->(b)
RETURN a.name, b.name
```

---

# View Attribute Lineage

```cypher
MATCH (a:Attribute)-[:DERIVED_FROM]->(b)
RETURN a.name, b.name
ORDER BY a.name
```

---

# View Multi-Hop Lineage

```cypher
MATCH path = (a:Attribute)-[:DERIVED_FROM*]->(b)
RETURN path
```

---

# View Join Relationships

```cypher
MATCH (a:QlikTable)-[r:JOINED_WITH]->(b)
RETURN a.name, r.type, b.name
```

---

# Clear Graph

```cypher
MATCH (n)
DETACH DELETE n
```

---

# Start FastAPI

```powershell
python -m uvicorn lineage_platform.api.app:app --reload
```

---

# Open Swagger Docs

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Health Check

```text
GET /health
```

---

## Node Metadata

```text
GET /api/v1/node/{node_id}
```

Returns:
- node metadata
- formulas
- relationships
- lineage connections

---

# Example API Response

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

# Enterprise Test Scenario

Recommended test file:

```text
99_enterprise_lineage_test.qvs
```

This validates:
- SQL lineage
- joins
- aggregations
- synthetic fields
- multi-hop lineage
- metadata APIs

---

# Current Supported Lineage

| Capability | Status |
|---|---|
| SQL Lineage | ✅ |
| RESIDENT Lineage | ✅ |
| JOIN Lineage | ✅ |
| Aggregation Lineage | ✅ |
| Synthetic Fields | ✅ |
| Multi-Hop Lineage | ✅ |
| Neo4j Graph | ✅ |
| Metadata APIs | ✅ |
| Attribute Lineage | ✅ |

---

# Known Limitations

## Current Parser Type

Current parser uses:
- regex
- line-based parsing

NOT:
- ANTLR grammar parsing

---

## Unsupported Complex Qlik Features

Some advanced enterprise patterns may still require:
- grammar-based parsing
- AST generation
- semantic analysis

Examples:
- nested subroutines
- macro execution
- dynamic variable expansion
- recursive includes

---

# Future Enhancements

## Planned Features

- Tableau lineage parsing
- Ab Initio lineage parsing
- Teradata BTEQ parsing
- Impact analysis APIs
- Search APIs
- Full lineage traversal APIs
- Graph visualization APIs
- Data quality metadata
- Business glossary integration
- Deterministic IDs
- ANTLR-based parser engine

---

# Recommended Neo4j Visualization Query

```cypher
MATCH path = (n)-[*1..4]-(m)
RETURN path
LIMIT 200
```

---

# Recommended Neo4j Styling

Set captions:
- `Attribute` → `name`
- `QlikTable` → `name`

Set colors:
- Attribute → blue
- QlikTable → green
- Table → orange

---

# Technology Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| Graph DB | Neo4j |
| SQL Parsing | sqlglot |
| Language | Python |
| Visualization | Neo4j Browser |
| Metadata Storage | Graph Model |

---

# License

Internal Enterprise Research / Educational Use