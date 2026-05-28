from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

# =========================================================
# SOURCE TYPES
# =========================================================


class SourceType(str, Enum):

    UNKNOWN = "UNKNOWN"

    SQL = "SQL"

    RESIDENT = "RESIDENT"

    FILE = "FILE"


# =========================================================
# QVW DASHBOARD MODELS
# =========================================================

@dataclass
class QVSChart:
    chart_id: str
    title: str
    fields: List[str] = field(default_factory=list)

@dataclass
class QVSSheet:
    sheet_id: str
    title: str
    charts: List[QVSChart] = field(default_factory=list)

# =========================================================
# QVS SUBROUTINE MODEL
# =========================================================

@dataclass
class QVSSubroutine:
    name: str
    body: str

# =========================================================
# QVS FIELD MODEL
# =========================================================


@dataclass
class QVSField:

    name: str

    table_name: Optional[str] = None

    formula: Optional[str] = None

    is_synthetic: bool = False

    source_fields: List[str] = field(default_factory=list)


# =========================================================
# QVS LOAD MODEL
# =========================================================


@dataclass
class QVSLoad:

    table_name: str

    fields: List[str] = field(default_factory=list)

    source_type: SourceType = SourceType.UNKNOWN

    source_table: Optional[str] = None

    sql_query: Optional[str] = None

    concatenates_to: Optional[str] = None


# =========================================================
# QVS JOIN MODEL
# =========================================================


@dataclass
class QVSJoin:

    join_type: str

    target_table: str

    source_table: str

    join_keys: List[str] = field(default_factory=list)


# =========================================================
# CONNECTION MODEL
# =========================================================


@dataclass
class QVSConnection:

    connection_name: str

    connection_string: Optional[str] = None

    database_type: Optional[str] = None


# =========================================================
# MAIN APPLICATION MODEL
# =========================================================


@dataclass
class QlikViewApp:

    app_name: str

    loads: List[QVSLoad] = field(default_factory=list)

    joins: List[QVSJoin] = field(default_factory=list)

    fields: List[QVSField] = field(default_factory=list)

    connections: List[QVSConnection] = field(default_factory=list)

    sheets: List[QVSSheet] = field(default_factory=list)

    subroutines: List[QVSSubroutine] = field(default_factory=list)

    dropped_tables: List[str] = field(default_factory=list)
