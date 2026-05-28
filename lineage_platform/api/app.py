from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =========================================================
# Route Imports
# =========================================================

from lineage_platform.api.routes.lineage_routes import router as lineage_router

from lineage_platform.api.routes.node_details import router as node_router

# =========================================================
# FastAPI App
# =========================================================

app = FastAPI(
    title="Enterprise Lineage Platform",
    description="""
    Enterprise metadata lineage platform supporting:

    - QlikView
    - Tableau
    - Teradata
    - Ab Initio
    - Neo4j lineage graph
    - Impact analysis
    - Attribute lineage
    - Metadata exploration
    """,
    version="2.1.0",
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# =========================================================
# Register Routers
# =========================================================

app.include_router(lineage_router, prefix="/api/v1", tags=["Lineage"])

app.include_router(node_router, prefix="/api/v1", tags=["Metadata"])

# =========================================================
# Root Endpoint
# =========================================================


@app.get("/")
def root():

    return {"application": "Enterprise Lineage Platform", "version": "2.1.0", "status": "running"}


# =========================================================
# Health Endpoint
# =========================================================


@app.get("/health")
def health():

    return {"status": "healthy"}
