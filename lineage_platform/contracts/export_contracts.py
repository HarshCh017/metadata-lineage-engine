from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SnapshotManifestV1(BaseModel):
    """
    Version 1 of the deterministic lineage export manifest.
    Immutable JSON contract for auditing and replay systems.
    """
    schema_version: str = "v1"
    as_of_timestamp: str = Field(..., description="ISO 8601 timestamp of the snapshot.")
    manifest_hash: str = Field(..., description="SHA-256 hash of the payload for integrity verification.")
    confidence_aggregate: float = Field(..., description="Overall confidence score of the lineage in this snapshot.")
    
    datasets: List[Dict[str, Any]] = Field(default_factory=list, description="All materialized datasets active in this snapshot.")
    transformations: List[Dict[str, Any]] = Field(default_factory=list, description="All active transformation paths.")

class OpenLineageExportV1(BaseModel):
    """
    Maps our internal graph to an OpenLineage-compatible event stream structure.
    """
    eventType: str = "COMPLETE"
    eventTime: str
    run: Dict[str, str]
    job: Dict[str, str]
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
