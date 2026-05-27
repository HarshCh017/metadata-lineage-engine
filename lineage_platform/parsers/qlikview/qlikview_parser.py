# lineage_platform/parsers/qlikview/qlikview_parser.py

import re
from pathlib import Path
from typing import Dict, List, Optional


class QVSLoad:
    """
    Represents a parsed LOAD block from a QlikView script.
    """

    def __init__(
        self,
        target_table: Optional[str] = None,
        source_type: Optional[str] = None,
        source_table: Optional[str] = None,
        fields: Optional[List[str]] = None,
        raw_sql: Optional[str] = None,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        self.target_table = target_table
        self.source_type = source_type
        self.source_table = source_table
        self.fields = fields or []
        self.raw_sql = raw_sql
        self.file_path = file_path
        self.operation = operation

    def to_dict(self):
        return {
            "target_table": self.target_table,
            "source_type": self.source_type,
            "source_table": self.source_table,
            "fields": self.fields,
            "raw_sql": self.raw_sql,
            "file_path": self.file_path,
            "operation": self.operation,
        }


class QlikViewParser:
    """
    Simple QlikView parser for testing lineage extraction.
    """

    def __init__(self):
        self.loads: List[QVSLoad] = []

    def parse_file(self, file_path: Path) -> Dict:
        """
        Parse a QVS file and extract lineage-related metadata.
        """

        print(f"\nParsing file: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        # Remove block comments like:
        

        content = re.sub(
            r"/\*.*?\*/",
            "",
            content,
            flags=re.DOTALL
        )

        # Remove REM comments like:
        # REM something ;

        content = re.sub(
            r"REM .*?;",
            "",
            content,
            flags=re.IGNORECASE
        )

        self.loads = []

        self._parse_load_blocks(content)

        return {
            "file_name": file_path.name,
            "total_loads": len(self.loads),
            "loads": [load.to_dict() for load in self.loads],
        }

    def _parse_load_blocks(self, content: str):
        """
        Parse LOAD statements from QVS content.
        """

        lines = content.splitlines()

        current_table = None
        current_block = []

        for line in lines:

            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Skip comments
            if stripped.startswith("//"):
                continue

            # Detect table label
            table_match = re.match(r"^([A-Za-z0-9_]+):$", stripped)

            if table_match:
                current_table = table_match.group(1)
                continue
            # Skip connection statements

            if stripped.upper().startswith("ODBC CONNECT"):
                continue

            if stripped.upper().startswith("OLEDB CONNECT"):
                continue

            if stripped.upper().startswith("LIB CONNECT"):
                continue
            current_block.append(stripped)

            # End of statement
            if stripped.endswith(";"):

                block_text = "\n".join(current_block)

                parsed = self._parse_single_block(
                    block_text,
                    current_table,
                )

                if parsed:
                    self.loads.append(parsed)

                current_block = []

    def _parse_single_block(
        self,
        block: str,
        target_table: Optional[str],
    ) -> Optional[QVSLoad]:
        """
        Parse individual LOAD block.
        """

        upper_block = block.upper()

        source_type = "UNKNOWN"
        source_table = None
        fields = []
        operation = None
        file_path = None

        # Detect JOIN
        if "LEFT JOIN" in upper_block:
            operation = "LEFT JOIN"

        elif "INNER JOIN" in upper_block:
            operation = "INNER JOIN"

        elif "NOCONCATENATE" in upper_block:
            operation = "NOCONCATENATE"

        elif "CONCATENATE" in upper_block:
            operation = "CONCATENATE"

        # Detect RESIDENT
        resident_match = re.search(
            r"RESIDENT\s+([A-Za-z0-9_]+)",
            block,
            re.IGNORECASE,
        )

        if resident_match:
            source_type = "RESIDENT"
            source_table = resident_match.group(1)

        # Detect FROM file
        from_match = re.search(
            r"FROM\s+[\[\'](.*?)[\]\']",
            block,
            re.IGNORECASE,
        )

        if from_match:
            source_type = "FILE"
            file_path = from_match.group(1)

        # Detect SQL SELECT
        if "SQL SELECT" in upper_block:
            source_type = "SQL"

            sql_match = re.search(
                r"SQL\s+SELECT(.*)",
                block,
                re.IGNORECASE | re.DOTALL,
            )

            if sql_match:
                source_table_match = re.search(
                    r"FROM\s+([A-Za-z0-9_.$()]+)",
                    sql_match.group(1),
                    re.IGNORECASE,
                )

                if source_table_match:
                    source_table = source_table_match.group(1)

        # Extract fields
        field_matches = re.findall(
            r"LOAD\s+(.*?)\s+(FROM|RESIDENT|SQL)",
            block,
            re.IGNORECASE | re.DOTALL,
        )

        if field_matches:

            raw_fields = field_matches[0][0]

            fields = [
                f.strip()
                for f in raw_fields.split(",")
                if f.strip()
            ]

        print(f"Detected source type: {source_type}")
        print(f"Detected source table: {source_table}")
        print(f"Detected operation: {operation}")

        return QVSLoad(
            target_table=target_table,
            source_type=source_type,
            source_table=source_table,
            fields=fields,
            raw_sql=block,
            file_path=file_path,
            operation=operation,
        )