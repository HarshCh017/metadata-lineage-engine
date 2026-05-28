from lineage_platform.neo4j.repository import LineageRepository
from lineage_platform.parsers.qlikview.antlr_parser import ANTLRQVSParser
import hashlib
from lineage_platform.observability.telemetry import TelemetryManager
from lineage_platform.core.normalization import SemanticNormalizer
from lineage_platform.core.incremental import IncrementalProcessor
from lineage_platform.neo4j.batch_writer import BatchGraphWriter
from lineage_platform.models.adapters import QlikToIntermediateAdapter
from lineage_platform.parsers.qlikview.qvw_parser import QVWParser
import time
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
import structlog
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = structlog.get_logger()


router = APIRouter()


class ParseRequest(BaseModel):
    script_path: str
    xml_metadata_path: Optional[str] = None
    overwrite: bool = False


# =========================================================
# Version Route
# =========================================================


@router.get("/version")
def version():
    return {"version": "2.1.0"}


@router.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# =========================================================
# Lineage Root
# =========================================================


@router.get("/lineage")
def lineage_root():

    return {"message": "Lineage API active"}


# =========================================================
# Parse Script Endpoint (§8 — enriched response)
# =========================================================


@router.post("/parse")
def parse_script(request: ParseRequest):
    logger.info("parse_script_start", script_path=request.script_path)
    file_path = Path(request.script_path)
    if not file_path.exists():
        logger.error("file_not_found", script_path=request.script_path)
        raise HTTPException(status_code=404, detail=f"File not found: {request.script_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Determine unique process ID (using hash of file path for stability)
    process_id = f"process_{hashlib.md5(request.script_path.encode()).hexdigest()[:16]}"

    # 1. Incremental Bypass Check
    repo = LineageRepository()
    incremental = IncrementalProcessor(repo.driver)
    hash_data = incremental.calculate_hash(content, dependencies=[])

    if not request.overwrite and not incremental.has_changed(process_id, hash_data["composite_hash"]):
        logger.info("parse_script_skipped", script_path=request.script_path, reason="hash_match")
        return {"status": "skipped", "reason": "hash_match"}

    # 2. Expire old graph components
    incremental.expire_script_subgraph(process_id)

    start_time = time.time()
    warnings: List[str] = []

    try:
        parser = ANTLRQVSParser()
        with TelemetryManager.PARSE_LATENCY.time():
            app, metadata = parser.parse(content)

        # Track parser telemetry
        if metadata.fallback_triggered:
            TelemetryManager.FALLBACK_RATES.inc()
            TelemetryManager.PARTIAL_RECOVERIES.inc()
            TelemetryManager.PARSER_CONFIDENCE.observe(50.0)  # Partial confidence
        else:
            TelemetryManager.PARSER_CONFIDENCE.observe(100.0)

        # Merge App details
        app.app_name = file_path.name

        if request.xml_metadata_path:
            qvw_parser = QVWParser()
            app.sheets = qvw_parser.parse_metadata(request.xml_metadata_path)

        # Adapter + Normalization
        intermediate_graph = QlikToIntermediateAdapter.transform(app)

        # Add process node explicitly to link lineage back to this script
        from lineage_platform.models.intermediate import ProcessNode
        p_node = ProcessNode(id=process_id, name=file_path.name, properties={"composite_hash": hash_data["composite_hash"]})
        intermediate_graph.processes.append(p_node)

        before_nodes = len(intermediate_graph.fields)
        intermediate_graph = SemanticNormalizer.normalize(intermediate_graph)
        after_nodes = len(intermediate_graph.fields)

        TelemetryManager.NORMALIZATION_MUTATIONS.inc(before_nodes - after_nodes)

        # Batch Write
        writer = BatchGraphWriter()
        with TelemetryManager.GRAPH_INSERT_LATENCY.time():
            writer.write_graph(intermediate_graph)
        writer.close()

        duration_ms = round((time.time() - start_time) * 1000, 2)
        TelemetryManager.FILES_PARSED.inc()

        logger.info("parse_script_success", app_name=app.app_name, loads=len(app.loads))
        return {
            "status": "success",
            "app_name": app.app_name,
            "engine": metadata.parser_engine,
            "duration_ms": duration_ms,
            "warnings": warnings,
        }
    except Exception as e:
        TelemetryManager.PARSE_FAILURES.inc()
        logger.error("parse_script_failed", error=str(e), script_path=request.script_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        repo.close()


@router.post("/parse/batch")
def parse_batch(requests: List[ParseRequest]):
    results = []
    for req in requests:
        try:
            res = parse_script(req)
            results.append(res)
        except Exception as e:
            results.append({"status": "error", "script_path": req.script_path, "detail": str(e)})
    return results
