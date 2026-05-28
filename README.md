# Metadata Lineage Engine

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Neo4j](https://img.shields.io/badge/neo4j-5.x-blue.svg)

An enterprise-grade, deterministic metadata parser that extracts deep data lineage from QlikView and other BI/SQL systems into a Neo4j graph database. Designed for cross-parser metadata merging, multi-level macro resolution, and seamless integration with Claude via an MCP plugin.

## 🏗 Architecture

The parsing pipeline is modular and robust:
`QVSParser` → `IncludeResolver` → `CommentCleaner` → `VariableParser` → `extract_load_blocks` → `GraphWriter`

- **Federated Governance & Policies:** Supports multi-domain namespace isolation, dynamic masking/redaction via the `GovernancePolicyEngine`, and explicit stewardship boundaries (`StewardshipManager`).
- **Distributed Reliability:** Includes an asynchronous `WorkloadManager` to govern query fanouts and ensure node starvation protection across enterprise topologies.
- **Enterprise Governance:** See [FEATURES.md](FEATURES.md) for details on Temporal Snapshotting, Trust Propagation, Compaction, and Corpus Validation.
- **Deep Lineage:** Extracts tables, fields, synthetic keys, subroutines, variables, and cross-dashboard dependencies.
- **SQL Parsing:** Extracts physical table and column-level lineage directly from embedded SQL queries.
- **Deterministic IDs:** Uses SHA-256 hashing (truncated to 16 chars) to guarantee consistent node identity across runs and between different parsers.
- **Observability:** Prometheus metrics + structlog for structured JSON logging.
- **Macro Expansion:** Recursively expands `$(var)` variables and `$(Include=...)` files up to configurable depths.

## 🚀 Quick Start & Guides

For detailed step-by-step usage, refer to the [USAGE GUIDE](USAGE_GUIDE.md).

### 1. Requirements
- Python 3.11
- Neo4j 5.x Database

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file (or copy `.env.example`):
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
QLIK_INCLUDE_ROOT=/path/to/shared/includes
QLIK_MAX_INCLUDE_DEPTH=10
STRICT_PARSING=false
```

### 4. Run the API
```bash
uvicorn lineage_platform.api.app:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker & Docker Compose

Run the entire stack (API + Neo4j) locally:
```bash
docker-compose up -d --build
```

The API will be available at `http://localhost:8000` and Neo4j Browser at `http://localhost:7474`.

## ☸️ Helm Chart Deployment

To deploy on Kubernetes:
```bash
helm install lineage-engine ./charts/metadata-lineage-engine -f values-prod.yaml
```

## 🔌 Claude MCP Plugin Usage

You can connect Claude Desktop to the Lineage Engine using the provided MCP server configuration.
Add this snippet to your `claude_desktop_config.json`:
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

## 📡 API Reference

- `POST /parse`: Parses a single script. Body: `{"script_path": "...", "xml_metadata_path": "..."}`
- `POST /parse/batch`: Parses multiple scripts. Body: `[{"script_path": "..."}]`
- `GET /health`: Basic health check
- `GET /version`: Returns current API version (2.1.0)
- `GET /metrics`: Prometheus metrics scrape endpoint
- `GET /lineage`: Root lineage status route

## 🕸️ Neo4j Schema Reference

### Node Labels
- `:QlikScript` - The source Qlik script file.
- `:Connection` - Extracted DB connection strings (ODBC, OLEDB, LIB, CUSTOM).
- `:QlikTable` - In-memory transformation table (transform layer).
- `:Table` - Physical database table (source layer).
- `:Attribute` - Fields and columns. Used for both Qlik fields and physical columns.
- `:Variable` - Variables defined via `SET` or `LET`.
- `:Subroutine` - Extracted subroutines from the script.
- `:QlikSheet` - UI Dashboard Sheets.
- `:QlikChart` - UI Dashboard Charts/Objects.

### Relationships
- `(QlikScript)-[:USES_CONNECTION]->(Connection)`
- `(QlikScript)-[:CONTAINS_TABLE]->(QlikTable)`
- `(QlikScript)-[:DEFINES_SUBROUTINE]->(Subroutine)`
- `(QlikScript)-[:CONTAINS_SHEET]->(QlikSheet)`
- `(QlikScript)-[:USES_VARIABLE]->(Variable)`
- `(QlikTable)-[:LOADS_FROM_TABLE]->(Table)`
- `(QlikTable)-[:HAS_FIELD]->(Attribute)`
- `(Table)-[:HAS_COLUMN]->(Attribute)` (Physical table to column mapping)
- `(Attribute)-[:DERIVES_FROM]->(Attribute)` (Lineage flow between fields/columns)
- `(QlikTable)-[:DERIVES_FROM_TABLE {via: 'resident'}]->(QlikTable)`
- `(QlikTable)-[:JOINS_WITH]->(QlikTable)`
- `(QlikTable)-[:CONCATENATES_INTO]->(QlikTable)`
- `(QlikSheet)-[:DISPLAYS_CHART]->(QlikChart)`
- `(QlikChart)-[:USES_FIELD]->(Attribute)`

## 🧪 Testing

The project uses a comprehensive enterprise validation suite including fuzzing, regression, semantic validations, and graph stress testing.

To run the entire governance validation suite, simply execute:
```bash
python run_enterprise_test.py
```

For a detailed breakdown of the test categories (fuzzing, corpus regression, stress tests, and semantic integrity), see the [TESTING GUIDE](TESTING_GUIDE.md).

## 📁 Project Structure

```
.
├── lineage_platform/
│   ├── api/          # FastAPI routes and models
│   ├── core/         # Cross-parser utilities (e.g., hashing)
│   ├── models/       # Shared Dataclass models
│   ├── neo4j/        # GraphWriter, Schema constraints
│   └── parsers/      # Modular parsers (QVS, QVW, SQL, etc.)
├── tests/            # pytest suite
├── charts/           # Kubernetes Helm charts
├── Dockerfile        # Multi-stage container build
├── docker-compose.yml# Local testing stack
└── requirements.txt  # Production dependencies
```

## 📜 License

MIT License. See [LICENSE](LICENSE) for more information.