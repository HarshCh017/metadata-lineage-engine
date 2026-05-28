# Metadata Lineage Engine - Enterprise Features

The Metadata Lineage Engine is a platform-grade parser and metadata extraction system built for scale. It transitions legacy Business Intelligence and Data Warehouse scripts into a deterministic, fully graph-traversable ontology.

## Core Capabilities

### 1. Multi-Stage Deterministic Parser
- **Abstract Syntax Tree (AST) Entrypoint**: Uses ANTLR4 for robust, deeply hierarchical tokenization and extraction.
- **Fail-Safe Regex Engine**: Automatically falls back to a highly-tuned regex traversal engine if AST limits are reached, ensuring zero metadata drops.
- **Cross-Platform**: Architected originally for QlikView but extensible to Snowflake, dbt, and other data warehouses.

### 2. Deep Lineage Extraction
- **Physical to Logical Mapping**: Traces physical database columns (`:Table`) into intermediate transformation layers (`:QlikTable`) and final Dashboard UI elements (`:QlikChart` / `:QlikSheet`).
- **Macro & Variable Resolution**: Recursively resolves and expands embedded `$(Include=...)` statements and dynamic variables (up to configurable nesting depths).
- **Embedded SQL Tracing**: Identifies and parses SQL strings embedded inside BI tool loads (e.g. `SQL SELECT * FROM ...`).

### 3. Enterprise Knowledge Graph (Neo4j)
- **High-Performance Batches**: Utilizes `apoc.periodic.iterate` (UNWIND) to insert tens of thousands of nodes and edges per second asynchronously.
- **Deterministic Hashing**: Utilizes SHA-256 (truncated to 16 hex chars) to consistently map fields, preventing graph duplication and allowing disparate parsers to merge identical physical tables seamlessly.
- **Semantic Normalization**: Automates casing and schema path deduplication, producing a perfectly stable ontology.

### 4. Interoperability & Open Standards
- **OpenLineage Support**: Native export functionality that abstracts the underlying graph into standard `RunEvent` specs (`GET /export/openlineage`).
- **Modular Intermediate Model**: The `GraphModel` acts as a middle-ware decoupling parsing logic from graph insertion logic.

### 5. Secure AI Integration (MCP)
- **Claude Desktop Native**: Ships with an MCP (Model Context Protocol) server to instantly grant AI agents deep context on your data landscape.
- **Defense-In-Depth Security**: The AI layer enforces `READ_ACCESS` driver boundaries, blocks mutative Cypher keywords (`CREATE`, `MERGE`, `DROP`), and bounds queries automatically with `LIMIT` and strict timeouts.

### 6. Production Observability
- **Prometheus Telemetry**: Real-time tracking of graph insert latencies, fallback rates, and throughput.
- **Structured Logging**: Deep JSON traces via `structlog` allowing Splunk/Datadog integration.
- **Automated Benchmarking**: Built-in CLI tools to track maximum memory allocation (via `tracemalloc`) and file parse MB/s directly out of the box.

### 7. Deployment Ready
- **Kubernetes**: Fully configured Helm charts for enterprise deployments.
- **Docker**: Simple `docker-compose` stacks for instant local deployment.
- **FastAPI Backend**: Fully asynchronous ReST interface powering the metadata ingestion.
