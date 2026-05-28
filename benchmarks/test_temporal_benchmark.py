import time
import structlog
from datetime import datetime
from lineage_platform.neo4j.repository import LineageRepository
from lineage_platform.models.snapshot import SnapshotContext

logger = structlog.get_logger()


def test_temporal_overhead():
    logger.info("Starting Temporal Query Overhead Benchmark...")

    repo = LineageRepository()

    # Generate mock queries (the DB will likely be empty or have synthetic data depending on if write was run first)
    start = time.time()

    # 1. Base Query (Active lineage)
    repo.search_tables("Table")
    base_duration = time.time() - start

    # 2. Temporal Query (Historical Snapshot)
    start = time.time()
    snapshot = SnapshotContext(as_of_timestamp=datetime.now().isoformat())
    repo.search_tables("Table", snapshot=snapshot)
    temporal_duration = time.time() - start

    logger.info("Base Query Duration", duration_sec=round(base_duration, 4))
    logger.info("Temporal Snapshot Query Duration", duration_sec=round(temporal_duration, 4))

    if base_duration > 0 and temporal_duration > 0:
        overhead = temporal_duration / base_duration
        logger.info("Temporal Overhead Multiplier", multiplier=round(overhead, 2))

    repo.close()


if __name__ == "__main__":
    test_temporal_overhead()
