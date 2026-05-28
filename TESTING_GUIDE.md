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