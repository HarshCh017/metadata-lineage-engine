from fastapi import APIRouter

router = APIRouter()

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
