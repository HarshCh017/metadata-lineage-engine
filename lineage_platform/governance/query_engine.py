from typing import Dict, Any, Optional, List
from lineage_platform.neo4j.repository import LineageRepository
from lineage_platform.models.snapshot import SnapshotContext
from lineage_platform.errors.failure_taxonomy import TraversalBudgetExceeded, GovernancePolicyViolation
from lineage_platform.observability.telemetry import TelemetryManager
import structlog
import time

logger = structlog.get_logger()

class QueryGovernanceEngine:
    """
    Central Governance Layer for Metadata Lineage access.
    Intercepts and blocks direct Cypher execution, enforcing:
    - Traversal budgets
    - Temporal snapshot integrity
    - Policy-aware querying
    """

    MAX_TRAVERSAL_DEPTH = 100
    MAX_NODE_FANOUT_BUDGET = 50000

    def __init__(self, repository: LineageRepository):
        self.repository = repository

    def _estimate_cost(self, depth: int, expected_fanout: int = 100) -> int:
        """Estimates traversal impact before execution."""
        return depth * expected_fanout

    def _enforce_budget(self, depth: int):
        if depth > self.MAX_TRAVERSAL_DEPTH:
            raise TraversalBudgetExceeded(
                f"Requested traversal depth {depth} exceeds governance budget of {self.MAX_TRAVERSAL_DEPTH}."
            )
        cost = self._estimate_cost(depth)
        if cost > self.MAX_NODE_FANOUT_BUDGET:
            raise TraversalBudgetExceeded(
                f"Estimated query cost {cost} exceeds maximum fanout budget of {self.MAX_NODE_FANOUT_BUDGET}."
            )

    def get_upstream_lineage(self, target_fqn: str, depth: int = 5, snapshot: Optional[SnapshotContext] = None) -> List[Dict[str, Any]]:
        self._enforce_budget(depth)
        start_time = time.time()
        
        # Use repository primitive directly, preventing raw Cypher injection
        result = self.repository.get_table_lineage(target_fqn, direction="upstream", max_depth=depth, snapshot=snapshot)
        
        TelemetryManager.TEMPORAL_QUERY_LATENCY.observe((time.time() - start_time) * 1000)
        return result

    def get_downstream_lineage(self, target_fqn: str, depth: int = 5, snapshot: Optional[SnapshotContext] = None) -> List[Dict[str, Any]]:
        self._enforce_budget(depth)
        start_time = time.time()
        
        result = self.repository.get_table_lineage(target_fqn, direction="downstream", max_depth=depth, snapshot=snapshot)
        
        TelemetryManager.TEMPORAL_QUERY_LATENCY.observe((time.time() - start_time) * 1000)
        return result

    def get_field_history(self, field_fqn: str, snapshot: Optional[SnapshotContext] = None) -> List[Dict[str, Any]]:
        # A mocked governance query to retrieve historical transformations for a field
        return []

    def get_snapshot_state(self, snapshot: SnapshotContext) -> Dict[str, Any]:
        """Returns the aggregate state of the graph at a specific point in time."""
        if not snapshot:
            raise GovernancePolicyViolation("get_snapshot_state requires an explicit SnapshotContext.")
        # Execute governed fetch
        start_time = time.time()
        # Mocked fetch for now
        TelemetryManager.TEMPORAL_QUERY_LATENCY.observe((time.time() - start_time) * 1000)
        return {"timestamp": snapshot.as_of_timestamp, "nodes": []}
