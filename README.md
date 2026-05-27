# Enterprise Metadata Lineage Engine

Enterprise-grade metadata lineage platform for parsing QlikView scripts and building attribute-level lineage graphs using Neo4j, FastAPI, and automated lineage extraction.

---

# Badges

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Neo4j](https://img.shields.io/badge/Neo4j-GraphDB-brightgreen)
![Pytest](https://img.shields.io/badge/Tests-Pytest-orange)
![Coverage](https://img.shields.io/badge/Coverage-66%25-yellow)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

---

# Overview

This project is an enterprise-style metadata lineage engine designed to parse QlikView scripts and generate graph-based lineage relationships inside Neo4j.

The platform supports:

- QlikView lineage parsing
- SQL lineage extraction
- Attribute-level lineage
- Multi-hop dependency tracking
- Synthetic field tracing
- Neo4j graph modeling
- FastAPI metadata APIs
- Automated testing & CI/CD

The project simulates real-world enterprise lineage systems used in large-scale data environments.

---

# Key Features

## QlikView Parsing

- SQL LOAD parsing
- RESIDENT LOAD parsing
- JOIN parsing
- CONCATENATE parsing
- GROUP BY parsing
- Synthetic field extraction
- Aggregation lineage
- ApplyMap lineage
- IF condition lineage

---

## Metadata Lineage

- Table-level lineage
- Attribute-level lineage
- Column lineage
- Derived field tracking
- Join lineage
- Multi-hop lineage traversal
- Source-to-target mapping

---

## Neo4j Graph Engine

- Graph-based metadata storage
- Relationship traversal
- Interactive graph visualization
- Metadata enrichment
- UUID node identification
- Lineage relationship modeling

---

## FastAPI Backend

- Metadata APIs
- Node detail APIs
- Health APIs
- Swagger/OpenAPI documentation

---

## Automated Testing

- Unit testing
- Integration testing
- Parser validation
- SQL parser tests
- Graph writer tests
- Fixture-based testing
- Coverage reporting

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

# Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| Graph Database | Neo4j |
| SQL Parsing | sqlglot |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Visualization | Neo4j Browser |

---

# Project Structure

```text
lineage-platform/
│
├── lineage_platform/
│   ├── api/
│   ├── batch/
│   ├── cli/
│   ├── core/
│   ├── lineage/
│   ├── models/
│   ├── neo4j/
│   └── parsers/
│
├── tests/
│   ├── api/
│   ├── fixtures/
│   ├── integration/
│   └── unit/
│
├── data/
├── .github/
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/HarshCh017/metadata-lineage-engine.git
cd metadata-lineage-engine
```

---

## Create Virtual Environment

```powershell
python -m venv .venv
```

---

## Activate Environment

```powershell
.\.venv\Scripts\Activate
```

---

## Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# Neo4j Setup

Install Neo4j Desktop:

https://neo4j.com/download/

Default configuration:

| Property | Value |
|---|---|
| Bolt URL | bolt://localhost:7687 |
| Browser | http://localhost:7474 |

---

# Environment Variables

Create:

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

# Running Enterprise Test Scenario

The repository includes:

```text
99_enterprise_lineage_test.qvs
```

which validates:

- SQL lineage
- joins
- aggregations
- synthetic fields
- multi-hop lineage
- metadata APIs

---

# Parse Enterprise Test File

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); print(app)"
```

---

# Load Lineage Graph into Neo4j

```powershell
python -c "from lineage_platform.parsers.qlikview.qvs_parser import QVSParser; from lineage_platform.neo4j.graph_writer import GraphWriter; parser = QVSParser(); app = parser.parse('data/input/qlikview/99_enterprise_lineage_test.qvs'); writer = GraphWriter(); writer.write_app(app); print('GRAPH WRITTEN SUCCESSFULLY')"
```

---

# Neo4j Queries

## View Entire Graph

```cypher
MATCH (n)
RETURN n
LIMIT 100
```

---

## View Attribute Lineage

```cypher
MATCH (a:Attribute)-[:DERIVED_FROM]->(b)
RETURN a.name, b.name
ORDER BY a.name
```

---

## View Multi-Hop Lineage

```cypher
MATCH path = (a:Attribute)-[:DERIVED_FROM*]->(b)
RETURN path
```

---

## View Join Relationships

```cypher
MATCH (a:QlikTable)-[r:JOINED_WITH]->(b)
RETURN a.name, r.type, b.name
```

---

# FastAPI Backend

## Start API Server

```powershell
python -m uvicorn lineage_platform.api.app:app --reload
```

---

## Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

---

# Example API Endpoints

| Endpoint | Description |
|---|---|
| `/health` | Health check |
| `/api/v1/node/{node_id}` | Node metadata |
| `/docs` | Swagger documentation |

---

# Testing

## Run All Tests

```powershell
pytest
```

---

## Run Coverage

```powershell
pytest --cov=lineage_platform
```

---

## Generate HTML Coverage Report

```powershell
pytest --cov=lineage_platform --cov-report=html
```

Open:

```text
htmlcov/index.html
```

---

# Current Test Coverage

```text
66%+
```

Coverage includes:

- parser validation
- integration tests
- SQL parser tests
- graph writer tests
- API tests
- synthetic lineage tests

---

# CI/CD

GitHub Actions automatically runs:

- pytest
- parser validation
- integration tests

on every push and pull request.

---

# Docker Support

## Build Container

```powershell
docker build -t metadata-lineage-engine .
```

---

## Run Container

```powershell
docker run -p 8000:8000 metadata-lineage-engine
```

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
| Automated Testing | ✅ |
| CI/CD | ✅ |

---

# Known Limitations

Current parser architecture uses:

- regex parsing
- line-based parsing

instead of:

- ANTLR grammar parsing
- full AST generation

Advanced enterprise Qlik features may require:
- semantic parsing
- recursive include resolution
- macro execution support

---

# Future Enhancements

- Tableau lineage parsing
- Ab Initio lineage parsing
- Teradata BTEQ parsing
- Impact analysis APIs
- Search APIs
- Graph traversal APIs
- Deterministic IDs
- ANTLR-based parser engine
- Data quality metadata
- Business glossary integration

---

# Recommended Neo4j Visualization

```cypher
MATCH path = (n)-[*1..4]-(m)
RETURN path
LIMIT 200
```

---

# License

Educational / Research / Portfolio Use