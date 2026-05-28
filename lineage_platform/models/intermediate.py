from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# =========================================================
# INTERMEDIATE METADATA MODEL
# =========================================================
# This model decouples source-specific parsing (Qlik, SQL, etc.)
# from graph persistence (Neo4j, OpenLineage, etc.).
# =========================================================

@dataclass
class FieldNode:
    id: str
    name: str
    data_type: str = "UNKNOWN"
    role: str = "dimension"
    formula: Optional[str] = None
    is_calculated: bool = False
    source_system: str = "UNKNOWN"
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DatasetNode:
    id: str
    name: str
    fully_qualified_name: str
    layer: str = "source" # source, transform, presentation
    source_system: str = "UNKNOWN"
    fields: List[FieldNode] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessNode:
    id: str
    name: str
    process_type: str = "script" # script, subroutine, query
    source_system: str = "UNKNOWN"
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LineageEdge:
    source_id: str
    target_id: str
    edge_type: str = "DERIVES_FROM" # DERIVES_FROM, LOADS_FROM
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DependencyEdge:
    source_id: str
    target_id: str
    edge_type: str = "CONTAINS" # CONTAINS, USES, JOINS
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphModel:
    datasets: List[DatasetNode] = field(default_factory=list)
    fields: List[FieldNode] = field(default_factory=list)
    processes: List[ProcessNode] = field(default_factory=list)
    lineage_edges: List[LineageEdge] = field(default_factory=list)
    dependency_edges: List[DependencyEdge] = field(default_factory=list)
