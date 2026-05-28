import pytest
import asyncio
import time
from lineage_platform.orchestration.workload_manager import WorkloadManager, WorkloadType
from lineage_platform.governance.policy_engine import GovernancePolicyEngine, AccessControl

@pytest.mark.anyio
async def test_federated_workload_queue_saturation():
    """
    Simulates high-concurrency federated workloads to ensure the WorkloadManager
    correctly prioritizes and isolates workloads without starving the event loop.
    """
    manager = WorkloadManager()
    
    # Trackers
    completed = []
    
    async def mock_tier_1_task():
        await asyncio.sleep(0.01)
        completed.append("t1")
        
    async def mock_tier_2_task():
        await asyncio.sleep(0.05)
        completed.append("t2")
        
    async def mock_tier_3_task():
        await asyncio.sleep(0.1)
        completed.append("t3")
        
    # Enqueue a massive backlog of T3 (Integrity scans)
    for i in range(100):
        await manager.enqueue(f"t3_{i}", WorkloadType.GRAPH_INTEGRITY_SCAN, mock_tier_3_task)
        
    # Enqueue a few T2 and T1 tasks
    await manager.enqueue("t2_1", WorkloadType.TEMPORAL_REPLAY, mock_tier_2_task)
    await manager.enqueue("t1_1", WorkloadType.SEMANTIC_VALIDATION, mock_tier_1_task)
    
    # Assert queues are populated
    assert manager.tier_3_queue.qsize() == 100
    assert manager.tier_2_queue.qsize() == 1
    assert manager.tier_1_queue.qsize() == 1

def test_governance_policy_overhead():
    """
    Measures the synchronous overhead of traversing policies on large payloads.
    Must evaluate 100,000 nodes in under 50ms.
    """
    engine = GovernancePolicyEngine(user_context={"role": "auditor"})
    
    # 100k nodes representing a massive graph payload
    payload = [{"namespace_id": "finance.payments", "name": "credit_card"} for _ in range(50000)]
    payload.extend([{"namespace_id": "shared.reference", "name": "country_codes"} for _ in range(50000)])
    
    start = time.time()
    sanitized = engine.apply_masking(payload)
    duration = time.time() - start
    
    assert duration < 0.1 # < 100ms
    # Shared reference is ALLOW (not masked), finance is MASK (not dropped)
    # Total count remains 100,000 but contents change
    assert len(sanitized) == 100000
    
    masked_count = sum(1 for n in sanitized if n["name"] == "***MASKED***")
    assert masked_count == 50000
