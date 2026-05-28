from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from enum import Enum

from datetime import datetime

# =========================================================
# INTERMEDIATE METADATA MODEL
# =========================================================
# This model decouples source-specific parsing (Qlik, SQL, etc.)
# from graph persistence (Neo4j, OpenLineage, etc.).
# =========================================================


@dataclass
class TemporalMixin:
    is_active: bool = field(default=True, kw_only=True)
    valid_from: Optional[datetime] = field(default=None, kw_only=True)
    valid_to: Optional[datetime] = field(default=None, kw_only=True)
    lineage_version: Optional[str] = field(default=None, kw_only=True)


@dataclass
class ProvenanceMixin:
    created_by_parser: str = field(default="UNKNOWN", kw_only=True)
    ast_node_type: Optional[str] = field(default=None, kw_only=True)


@dataclass
class GovernanceMixin:
    namespace_id: str = field(default="default", kw_only=True)
    domain_owner: str = field(default="UNKNOWN", kw_only=True)
    sensitivity_level: str = field(default="PUBLIC", kw_only=True)
    governance_scope: str = field(default="GLOBAL", kw_only=True)
    trust_zone: str = field(default="UNVERIFIED", kw_only=True)


class TransformationType(str, Enum):
    AGGREGATION = "AGGREGATION"
    FILTER = "FILTER"
    CASE = "CASE"
    JOIN = "JOIN"
    WINDOW = "WINDOW"
    CAST = "CAST"
    ARITHMETIC = "ARITHMETIC"
    MACRO = "MACRO"
    LOOKUP = "LOOKUP"
    CONCAT = "CONCAT"
    UNKNOWN = "UNKNOWN"


@dataclass
class TransformationNode(TemporalMixin, ProvenanceMixin, GovernanceMixin):
    id: str
    expression: str
    transformation_type: TransformationType = TransformationType.UNKNOWN
    source_parser: str = "UNKNOWN"
    lineage_depth: int = 1
    deterministic: bool = True
    aggregate: bool = False
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FieldNode(TemporalMixin, ProvenanceMixin):
    id: str
    name: str
    data_type: str = "UNKNOWN"
    role: str = "dimension"
    formula: Optional[str] = None
    is_calculated: bool = False
    source_system: str = "UNKNOWN"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetNode(TemporalMixin, ProvenanceMixin, GovernanceMixin):
    id: str
    name: str
    fully_qualified_name: str
    layer: str = "source"  # source, transform, presentation
    source_system: str = "UNKNOWN"
    fields: List[FieldNode] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessNode(TemporalMixin, ProvenanceMixin):
    id: str
    name: str
    process_type: str = "script"  # script, subroutine, query
    source_system: str = "UNKNOWN"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageEdge(TemporalMixin, ProvenanceMixin, GovernanceMixin):
    source_id: str
    target_id: str
    edge_type: str = "DERIVES_FROM"  # DERIVES_FROM, LOADS_FROM
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyEdge:
    source_id: str
    target_id: str
    edge_type: str = "CONTAINS"  # CONTAINS, USES, JOINS
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphModel:
    datasets: List[DatasetNode] = field(default_factory=list)
    fields: List[FieldNode] = field(default_factory=list)
    processes: List[ProcessNode] = field(default_factory=list)
    transformations: List[TransformationNode] = field(default_factory=list)
    lineage_edges: List[LineageEdge] = field(default_factory=list)
    dependency_edges: List[DependencyEdge] = field(default_factory=list)
