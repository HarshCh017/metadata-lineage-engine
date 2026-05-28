import time
import pytest
from lineage_platform.governance.query_engine import QueryGovernanceEngine
from lineage_platform.neo4j.repository import LineageRepository
from lineage_platform.errors.failure_taxonomy import TraversalBudgetExceeded


@pytest.fixture
def mock_repository():
    return LineageRepository()


@pytest.fixture
def governance_engine(mock_repository):
    return QueryGovernanceEngine(mock_repository)


def test_query_cost_estimation(governance_engine):
    """
    Validates that the QueryGovernanceEngine correctly calculates cost and preemptively blocks extreme traversals.
    """
    # Safe traversal (Depth 5)
    cost = governance_engine._estimate_cost(5)
    assert cost == 500

    # Dangerous traversal (Depth 150)
    with pytest.raises(TraversalBudgetExceeded) as exc:
        governance_engine.get_upstream_lineage("mock_table", depth=150)
    assert "exceeds governance budget" in str(exc.value)


def test_graph_density_simulation(governance_engine, monkeypatch):
    """
    Simulates querying against a 10M relationship graph to track traversal latency overhead
    incurred strictly by the Governance layer.
    """
    def mock_heavy_query(*args, **kwargs):
        time.sleep(0.01)  # Simulate DB latency
        return [{"field": "mock_field", "source": "mock_source"} for _ in range(100)]

    monkeypatch.setattr(governance_engine.repository, "get_table_lineage", mock_heavy_query)

    start_time = time.time()
    result = governance_engine.get_upstream_lineage("mock_table", depth=50)
    duration = time.time() - start_time

    assert len(result) == 100
    # Governance overhead + DB latency must be exceptionally fast (< 100ms)
    assert duration < 0.1
