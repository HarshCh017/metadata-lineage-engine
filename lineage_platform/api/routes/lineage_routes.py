import time
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
import structlog
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, REGISTRY

logger = structlog.get_logger()

from lineage_platform.parsers.qlikview.qvs_parser import QVSParser
from lineage_platform.parsers.qlikview.qvw_parser import QVWParser
from lineage_platform.models.adapters import QlikToIntermediateAdapter
from lineage_platform.neo4j.batch_writer import BatchGraphWriter

# Prometheus counters (§12)
try:
    FILES_PARSED = Counter("qlikview_files_parsed_total", "Total QlikView files parsed")
    PARSE_FAILURES = Counter("qlikview_parse_failures_total", "Total parse failures")
    INCLUDES_RESOLVED = Counter("qlikview_includes_resolved_total", "Total $(Include=...) directives resolved")
    MACRO_EXPANSIONS = Counter("qlikview_macro_expansions_total", "Total $(var) macro expansions performed")
except ValueError:
    # Handle duplicate registration during pytest re-imports
    FILES_PARSED = REGISTRY._names_to_collectors["qlikview_files_parsed_total"]
    PARSE_FAILURES = REGISTRY._names_to_collectors["qlikview_parse_failures_total"]
    INCLUDES_RESOLVED = REGISTRY._names_to_collectors["qlikview_includes_resolved_total"]
    MACRO_EXPANSIONS = REGISTRY._names_to_collectors["qlikview_macro_expansions_total"]

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

    start_time = time.time()
    warnings = []

    try:
        parser = QVSParser()
        app = parser.parse(str(file_path))

        if request.xml_metadata_path:
            qvw_parser = QVWParser()
            app.sheets = qvw_parser.parse_metadata(request.xml_metadata_path)

        intermediate_graph = QlikToIntermediateAdapter.transform(app)
        writer = BatchGraphWriter()
        writer.write_graph(intermediate_graph)
        writer.close()

        duration_ms = round((time.time() - start_time) * 1000, 2)
        FILES_PARSED.inc()

        logger.info("parse_script_success", app_name=app.app_name, loads=len(app.loads))
        return {
            "status": "success",
            "app_name": app.app_name,
            "qlik_tables": len(app.loads),
            "physical_tables": len(set(l.source_table for l in app.loads if l.source_table)),
            "attributes": sum(len(l.fields) for l in app.loads),
            "joins": len(app.joins),
            "concatenates": sum(1 for l in app.loads if l.concatenates_to),
            "variables": len(app.variables),
            "subroutines": len(app.subroutines),
            "sheets": len(app.sheets),
            "charts": sum(len(s.charts) for s in app.sheets),
            "connections": len(app.connections),
            "dropped_tables": len(app.dropped_tables),
            "dropped_fields": len(app.dropped_fields),
            "duration_ms": duration_ms,
            "warnings": warnings,
        }
    except Exception as e:
        PARSE_FAILURES.inc()
        logger.error("parse_script_failed", error=str(e), script_path=request.script_path)
        raise HTTPException(status_code=500, detail=str(e))


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
