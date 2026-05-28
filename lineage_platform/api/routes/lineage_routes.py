from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
import structlog
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = structlog.get_logger()

from lineage_platform.parsers.qlikview.qvs_parser import QVSParser
from lineage_platform.parsers.qlikview.qvw_parser import QVWParser
from lineage_platform.neo4j.graph_writer import GraphWriter

router = APIRouter()

class ParseRequest(BaseModel):
    script_path: str
    xml_metadata_path: Optional[str] = None
    overwrite: bool = False

# =========================================================
# Health Route
# =========================================================


@router.get("/health")
def health():
    return {"status": "healthy"}

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
# Parse Script Endpoint
# =========================================================

@router.post("/parse")
def parse_script(request: ParseRequest):
    logger.info("parse_script_start", script_path=request.script_path)
    file_path = Path(request.script_path)
    if not file_path.exists():
        logger.error("file_not_found", script_path=request.script_path)
        raise HTTPException(status_code=404, detail=f"File not found: {request.script_path}")
    
    try:
        parser = QVSParser()
        app = parser.parse(str(file_path))
        
        if request.xml_metadata_path:
            qvw_parser = QVWParser()
            app.sheets = qvw_parser.parse_metadata(request.xml_metadata_path)
            
        
        writer = GraphWriter()
        writer.write_app(app)
        
        logger.info("parse_script_success", app_name=app.app_name, loads=len(app.loads))
        return {
            "status": "success",
            "app_name": app.app_name,
            "loads_processed": len(app.loads),
            "connections_processed": len(app.connections)
        }
    except Exception as e:
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
