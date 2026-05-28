import re
from pathlib import Path
from typing import List, Optional

from lineage_platform.models.qlik_models import QVSLoad, QlikViewApp, SourceType, QVSSubroutine

from lineage_platform.parsers.qlikview.field_parser import FieldParser

from lineage_platform.parsers.qlikview.join_parser import JoinParser

from lineage_platform.parsers.qlikview.synthetic_field_parser import SyntheticFieldParser

from lineage_platform.parsers.qlikview.connection_parser import ConnectionParser

from lineage_platform.parsers.qlikview.comment_cleaner import CommentCleaner
from lineage_platform.parsers.qlikview.variable_parser import VariableParser
from lineage_platform.parsers.qlikview.include_resolver import IncludeResolver

from lineage_platform.parsers.qlikview.sql_parser import SQLParser


class QVSParser:
    """
    Enterprise-safe QlikView parser.
    """

    def __init__(self):

        self.field_parser = FieldParser()
        self.join_parser = JoinParser()
        self.synthetic_parser = SyntheticFieldParser()
        self.connection_parser = ConnectionParser()

    # =====================================================
    # MAIN PARSE METHOD
    # =====================================================

    def parse(self, file_path: str) -> QlikViewApp:

        path = Path(file_path)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:

            content = f.read()

        # -------------------------------------------------
        # Resolve includes
        # -------------------------------------------------

        content = IncludeResolver.resolve_includes(content, path)

        # -------------------------------------------------
        # Clean comments
        # -------------------------------------------------

        content = CommentCleaner.clean_comments(content)

        # -------------------------------------------------
        # Extract subroutines
        # -------------------------------------------------

        subroutines = []
        def replace_sub(match):
            name = match.group(1).strip()
            body = match.group(2).strip()
            subroutines.append(QVSSubroutine(name=name, body=body))
            return ""
            
        content = re.sub(r"^\s*SUB\s+([A-Za-z0-9_]+)(.*?)\bEND\s+SUB\b", replace_sub, content, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)

        # -------------------------------------------------
        # Extract variables and expand macros
        # -------------------------------------------------

        variables = VariableParser.extract_variables(content)
        content = VariableParser.expand_macros(content, variables)

        # -------------------------------------------------
        # Create app
        # -------------------------------------------------

        app = QlikViewApp(app_name=path.stem)
        app.subroutines = subroutines

        # -------------------------------------------------
        # Parse connections
        # -------------------------------------------------

        app.connections = self.connection_parser.extract_connections(content)

        # -------------------------------------------------
        # Extract LOAD blocks
        # -------------------------------------------------

        load_blocks = self.extract_load_blocks(content)

        # -------------------------------------------------
        # Parse LOAD blocks
        # -------------------------------------------------

        last_table_name = None

        for block in load_blocks:

            load = self.parse_load_block(block)

            if load:

                app.loads.append(load)

                last_table_name = load.table_name

            # ---------------------------------------------
            # Parse joins
            # ---------------------------------------------

            joins = self.join_parser.extract_joins(block, last_table_name)

            app.joins.extend(joins)

            # ---------------------------------------------
            # Parse synthetic fields
            # ---------------------------------------------

            synthetic_fields = self.synthetic_parser.extract_synthetic_fields(block, load.table_name if load else None)

            app.fields.extend(synthetic_fields)

        return app

    # =====================================================
    # ENTERPRISE LOAD BLOCK EXTRACTION
    # =====================================================

    def extract_load_blocks(self, script_content: str) -> List[str]:
        """
        Enterprise-safe LOAD block extraction.

        Handles:
        - SQL LOAD
        - RESIDENT LOAD
        - JOIN LOAD
        - GROUP BY
        - CONCATENATE
        - multiline statements
        """

        lines = script_content.splitlines()

        blocks = []

        current_block: List[str] = []

        inside_load = False

        for line in lines:

            stripped = line.strip()

            # ---------------------------------------------
            # Skip empty lines
            # ---------------------------------------------

            if not stripped:
                continue

            upper = stripped.upper()

            # ---------------------------------------------
            # Detect table labels
            # Example:
            # CustomerMaster:
            # ---------------------------------------------

            table_label_match = re.match(r"^([A-Za-z0-9_]+)\s*:$", stripped)

            if table_label_match:

                # Save previous block

                if current_block:

                    blocks.append("\n".join(current_block))

                    current_block = []

                current_block.append(stripped)

                continue

            # ---------------------------------------------
            # Detect LOAD block start
            # ---------------------------------------------

            load_start_keywords = [
                "LOAD",
                "LEFT JOIN",
                "RIGHT JOIN",
                "INNER JOIN",
                "OUTER JOIN",
                "FULL JOIN",
                "CONCATENATE",
            ]

            if any(upper.startswith(keyword) for keyword in load_start_keywords):

                inside_load = True

            # ---------------------------------------------
            # Capture block
            # ---------------------------------------------

            if inside_load or current_block:

                current_block.append(line)

                # -----------------------------------------
                # End block on semicolon
                # -----------------------------------------

                if stripped.endswith(";"):

                    blocks.append("\n".join(current_block))

                    current_block = []

                    inside_load = False

        # -------------------------------------------------
        # Final safety
        # -------------------------------------------------

        if current_block:

            blocks.append("\n".join(current_block))

        return blocks

    # =====================================================
    # PARSE LOAD BLOCK
    # =====================================================

    def parse_load_block(self, block: str) -> Optional[QVSLoad]:
        """
        Parse a single LOAD block.
        """

        # -------------------------------------------------
        # Extract table name
        # -------------------------------------------------

        table_match = re.search(r"^([A-Za-z0-9_]+)\s*:", block, flags=re.MULTILINE)

        if table_match:

            table_name = table_match.group(1)

        else:

            table_name = "UNKNOWN_TABLE"

        # -------------------------------------------------
        # Extract fields
        # -------------------------------------------------

        fields = self.field_parser.extract_fields(block)

        # -------------------------------------------------
        # Detect source type
        # -------------------------------------------------

        source_type = SourceType.UNKNOWN

        source_table = None

        sql_query = None

        concatenates_to = None

        # -------------------------------------------------
        # CONCATENATE
        # -------------------------------------------------

        concat_match = re.search(r"CONCATENATE\s*\(\s*([A-Za-z0-9_]+)\s*\)", block, flags=re.IGNORECASE)
        if concat_match:
            concatenates_to = concat_match.group(1)

        # -------------------------------------------------
        # SQL SOURCE
        # -------------------------------------------------

        sql_match = re.search(r"(SELECT.*?FROM.*?;)", block, flags=(re.IGNORECASE | re.DOTALL))

        if sql_match:

            source_type = SourceType.SQL

            sql_query = sql_match.group(1)

            sql_tables = SQLParser.extract_sql_tables(sql_query)

            if sql_tables:

                source_table = sql_tables[0]

        # -------------------------------------------------
        # RESIDENT SOURCE
        # -------------------------------------------------

        resident_match = re.search(r"RESIDENT\s+([A-Za-z0-9_]+)", block, flags=re.IGNORECASE)

        if resident_match:

            source_type = SourceType.RESIDENT

            source_table = resident_match.group(1)

        # -------------------------------------------------
        # FILE SOURCE
        # -------------------------------------------------

        from_match = re.search(r'FROM\s+[\'"](.+?)[\'"]', block, flags=re.IGNORECASE)

        if from_match:

            source_type = SourceType.FILE

            source_table = from_match.group(1)

        # -------------------------------------------------
        # Build Load Object
        # -------------------------------------------------

        if source_type == SourceType.UNKNOWN and not fields:

            return None

        return QVSLoad(
            table_name=table_name,
            fields=fields,
            source_type=source_type,
            source_table=source_table,
            sql_query=sql_query,
            concatenates_to=concatenates_to,
        )
