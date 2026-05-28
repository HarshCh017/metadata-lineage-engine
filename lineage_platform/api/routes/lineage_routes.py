from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path

from lineage_platform.parsers.qlikview.qvs_parser import QVSParser
from lineage_platform.neo4j.graph_writer import GraphWriter

router = APIRouter()

class ParseRequest(BaseModel):
    script_path: str
    overwrite: bool = False

# =========================================================
# Health Route
# =========================================================


@router.get("/health")
def health():

    return {"status": "healthy"}


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
    file_path = Path(request.script_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.script_path}")
    
    try:
        parser = QVSParser()
        app = parser.parse(str(file_path))
        
        writer = GraphWriter()
        writer.write_app(app)
        
        return {
            "status": "success",
            "app_name": app.app_name,
            "loads_processed": len(app.loads),
            "connections_processed": len(app.connections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
