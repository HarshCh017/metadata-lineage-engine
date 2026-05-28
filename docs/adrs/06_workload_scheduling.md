# ADR 06: Workload Scheduling Guarantees

## Status
Accepted

## Context
The platform executes heavy, graph-intensive workloads like `GRAPH_INTEGRITY_SCAN` and `TEMPORAL_REPLAY`. These workloads risk resource starvation if not scheduled properly.

## Decision
We implement a **Priority-Tiered asyncio Event Loop** architecture for Phase 14, serving as a placeholder for a future distributed queue (e.g. Celery/RabbitMQ).
- **Tier 1 (High):** API queries, Telemetry, Governance Auth.
- **Tier 2 (Medium):** Point-in-time Replays, Drift Analysis.
- **Tier 3 (Low - Throttled):** Full Graph Integrity Scans, Bulk Export Compactions.
- Replays must never starve Tier 1. Integrity Scans must backoff if Tier 2 is saturated.

## Consequences
- Retains single-node execution simplicity for this phase while strictly enforcing distributed semantic boundaries.
- Prepares the platform for a seamless transition to a true distributed worker pool in the future.
