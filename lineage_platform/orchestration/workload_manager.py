import asyncio
from enum import Enum
from typing import Dict, Any, Callable
from lineage_platform.observability.telemetry import TelemetryManager
from lineage_platform.errors.failure_taxonomy import WorkloadStarvationFailure
import structlog
import time

logger = structlog.get_logger()

class WorkloadType(str, Enum):
    TEMPORAL_REPLAY = "TEMPORAL_REPLAY"
    GRAPH_INTEGRITY_SCAN = "GRAPH_INTEGRITY_SCAN"
    SEMANTIC_VALIDATION = "SEMANTIC_VALIDATION"
    DRIFT_ANALYSIS = "DRIFT_ANALYSIS"
    COMPACTION = "COMPACTION"
    BULK_EXPORT = "BULK_EXPORT"

class WorkloadState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    THROTTLED = "THROTTLED"

class WorkloadManager:
    """
    In-memory async workload orchestrator.
    Serves as the Phase 14 precursor to a distributed Celery/RabbitMQ architecture.
    """
    def __init__(self):
        self.active_workloads: Dict[str, WorkloadState] = {}
        # Priority tiers as defined in ADR-06
        self.tier_1_queue = asyncio.Queue()  # Telemetry, API
        self.tier_2_queue = asyncio.Queue()  # Replays, Drift
        self.tier_3_queue = asyncio.Queue()  # Scans, Compaction
        
    async def enqueue(self, workload_id: str, workload_type: WorkloadType, task: Callable):
        self.active_workloads[workload_id] = WorkloadState.QUEUED
        
        if workload_type in [WorkloadType.TEMPORAL_REPLAY, WorkloadType.DRIFT_ANALYSIS]:
            await self.tier_2_queue.put((workload_id, task))
        elif workload_type in [WorkloadType.GRAPH_INTEGRITY_SCAN, WorkloadType.COMPACTION, WorkloadType.BULK_EXPORT]:
            await self.tier_3_queue.put((workload_id, task))
        else:
            await self.tier_1_queue.put((workload_id, task))
            
        TelemetryManager.WORKLOAD_QUEUE_DEPTH.inc()
        logger.info("workload_enqueued", workload_id=workload_id, type=workload_type)

    async def _execute_task(self, workload_id: str, task: Callable):
        self.active_workloads[workload_id] = WorkloadState.RUNNING
        try:
            # Async execution
            await task()
            self.active_workloads[workload_id] = WorkloadState.COMPLETED
        except Exception as e:
            self.active_workloads[workload_id] = WorkloadState.FAILED
            logger.error("workload_failed", workload_id=workload_id, error=str(e))
        finally:
            TelemetryManager.WORKLOAD_QUEUE_DEPTH.dec()
