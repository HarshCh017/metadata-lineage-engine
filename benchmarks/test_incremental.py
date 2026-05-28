import time
import structlog
from lineage_platform.core.incremental import IncrementalProcessor
from lineage_platform.neo4j.repository import LineageRepository
from lineage_platform.models.qlik_models import QlikViewApp
from lineage_platform.models.adapters import QlikToIntermediateAdapter
from lineage_platform.neo4j.batch_writer import BatchGraphWriter
import hashlib

logger = structlog.get_logger()


def test_incremental_refresh():
    logger.info("Starting Incremental Refresh Benchmark...")

    # 1. Setup Mock Payload
    content = "LOAD * FROM [mock_table.csv]; " * 1000  # Large mock
    process_id = f"process_{hashlib.md5(content.encode()).hexdigest()[:16]}"

    repo = LineageRepository()
    incremental = IncrementalProcessor(repo.driver)

    # 2. Force First Parse (Full Refresh)
    start = time.time()

    hash_data = incremental.calculate_hash(content, dependencies=[])
    app = QlikViewApp(app_name="benchmark_incremental")
    graph = QlikToIntermediateAdapter.transform(app)
    from lineage_platform.models.intermediate import ProcessNode
    graph.processes.append(ProcessNode(id=process_id, name="bench", properties={"composite_hash": hash_data["composite_hash"]}))

    writer = BatchGraphWriter()
    writer.write_graph(graph)
    writer.close()

    full_duration = time.time() - start
    logger.info("Full Refresh Duration", duration_sec=round(full_duration, 4))

    # 3. Trigger Incremental (Bypass)
    start = time.time()

    incremental.has_changed(process_id, hash_data["composite_hash"])

    incremental_duration = time.time() - start
    logger.info("Incremental Bypass Duration", duration_sec=round(incremental_duration, 4))

    if incremental_duration > 0 and full_duration > 0:
        speedup = full_duration / incremental_duration
        logger.info("Incremental Speedup", multiplier=round(speedup, 2))

    repo.close()


if __name__ == "__main__":
    test_incremental_refresh()
