from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class SnapshotContext:
    """
    Governance-grade Context for querying historical graph states.
    If provided, the repository will automatically inject temporal filters 
    to reconstruct the lineage exactly as it existed at 'as_of_timestamp'.
    """
    as_of_timestamp: Optional[str] = None # ISO format timestamp
    snapshot_id: Optional[str] = None # Immutable audit state ID
