import re
from pathlib import Path
from typing import List, Optional

from lineage_platform.models.qlik_models import (
    QVSLoad,
    QVSJoin,
    QVSField,
    QlikViewApp,
    SourceType
)

from lineage_platform.parsers.qlikview.field_parser import (
    FieldParser
)

from lineage_platform.parsers.qlikview.join_parser import (
    JoinParser
)

from lineage_platform.parsers.qlikview.synthetic_field_parser import (
    SyntheticFieldParser
)

from lineage_platform.parsers.qlikview.connection_parser import (
    ConnectionParser
)

from lineage_platform.parsers.qlikview.sql_parser import (
    SQLParser
)


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

    def parse(
        self,
        file_path: str
    ) -> QlikViewApp:

        path = Path(file_path)

        with open(
            path,
            'r',
            encoding='utf-8',
            errors='ignore'
        ) as f:

            content = f.read()

        # -------------------------------------------------
        # Clean comments
        # -------------------------------------------------

        content = self.remove_comments(
            content
        )

        # -------------------------------------------------
        # Create app
        # -------------------------------------------------

        app = QlikViewApp(
            app_name=path.stem
        )

        # -------------------------------------------------
        # Parse connections
        # -------------------------------------------------

        app.connections = (
            self.connection_parser
            .extract_connections(content)
        )

        # -------------------------------------------------
        # Extract LOAD blocks
        # -------------------------------------------------

        load_blocks = (
            self.extract_load_blocks(
                content
            )
        )

        # -------------------------------------------------
        # Parse LOAD blocks
        # -------------------------------------------------

        last_table_name = None

        for block in load_blocks:

            load = self.parse_load_block(
                block
            )

            if load:

                app.loads.append(
                    load
                )

                last_table_name = (
                    load.table_name
                )

            # ---------------------------------------------
            # Parse joins
            # ---------------------------------------------

            joins = self.join_parser.extract_joins(
                block,
                last_table_name
            )

            app.joins.extend(
                joins
            )

            # ---------------------------------------------
            # Parse synthetic fields
            # ---------------------------------------------

            synthetic_fields = (
                self.synthetic_parser
                .extract_synthetic_fields(
                    block,
                    load.table_name
                    if load else None
                )
            )

            app.fields.extend(
                synthetic_fields
            )

        return app

    # =====================================================
    # REMOVE COMMENTS
    # =====================================================

    def remove_comments(
        self,
        content: str
    ) -> str:

        # -------------------------------------------------
        # Remove block comments
        # -------------------------------------------------

        content = re.sub(
            r'/\*.*?\*/',
            '',
            content,
            flags=re.DOTALL
        )

        # -------------------------------------------------
        # Remove single-line comments
        # -------------------------------------------------

        cleaned_lines = []

        for line in content.splitlines():

            stripped = line.strip()

            if stripped.startswith('//'):
                continue

            cleaned_lines.append(
                line
            )

        return '\n'.join(
            cleaned_lines
        )

    # =====================================================
    # ENTERPRISE LOAD BLOCK EXTRACTION
    # =====================================================

    def extract_load_blocks(
        self,
        script_content: str
    ) -> List[str]:

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

        current_block = []

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

            table_label_match = re.match(
                r'^([A-Za-z0-9_]+)\s*:$',
                stripped
            )

            if table_label_match:

                # Save previous block

                if current_block:

                    blocks.append(
                        '\n'.join(current_block)
                    )

                    current_block = []

                current_block.append(
                    stripped
                )

                continue

            # ---------------------------------------------
            # Detect LOAD block start
            # ---------------------------------------------

            load_start_keywords = [

                'LOAD',
                'LEFT JOIN',
                'RIGHT JOIN',
                'INNER JOIN',
                'OUTER JOIN',
                'FULL JOIN',
                'CONCATENATE'

            ]

            if any(
                upper.startswith(keyword)
                for keyword in load_start_keywords
            ):

                inside_load = True

            # ---------------------------------------------
            # Capture block
            # ---------------------------------------------

            if inside_load or current_block:

                current_block.append(
                    line
                )

                # -----------------------------------------
                # End block on semicolon
                # -----------------------------------------

                if stripped.endswith(';'):

                    blocks.append(
                        '\n'.join(current_block)
                    )

                    current_block = []

                    inside_load = False

        # -------------------------------------------------
        # Final safety
        # -------------------------------------------------

        if current_block:

            blocks.append(
                '\n'.join(current_block)
            )

        return blocks

    # =====================================================
    # PARSE LOAD BLOCK
    # =====================================================

    def parse_load_block(
        self,
        block: str
    ) -> Optional[QVSLoad]:

        """
        Parse a single LOAD block.
        """

        # -------------------------------------------------
        # Extract table name
        # -------------------------------------------------

        table_match = re.search(
            r'^([A-Za-z0-9_]+)\s*:',
            block,
            flags=re.MULTILINE
        )

        if table_match:

            table_name = (
                table_match.group(1)
            )

        else:

            table_name = (
                'UNKNOWN_TABLE'
            )

        # -------------------------------------------------
        # Extract fields
        # -------------------------------------------------

        fields = (
            self.field_parser
            .extract_fields(block)
        )

        # -------------------------------------------------
        # Detect source type
        # -------------------------------------------------

        source_type = (
            SourceType.UNKNOWN
        )

        source_table = None

        sql_query = None

        # -------------------------------------------------
        # SQL SOURCE
        # -------------------------------------------------

        sql_match = re.search(
            r'(SELECT.*?FROM.*?;)',
            block,
            flags=(
                re.IGNORECASE |
                re.DOTALL
            )
        )

        if sql_match:

            source_type = (
                SourceType.SQL
            )

            sql_query = (
                sql_match.group(1)
            )

            sql_tables = (
                SQLParser
                .extract_sql_tables(
                    sql_query
                )
            )

            if sql_tables:

                source_table = (
                    sql_tables[0]
                )

        # -------------------------------------------------
        # RESIDENT SOURCE
        # -------------------------------------------------

        resident_match = re.search(
            r'RESIDENT\s+([A-Za-z0-9_]+)',
            block,
            flags=re.IGNORECASE
        )

        if resident_match:

            source_type = (
                SourceType.RESIDENT
            )

            source_table = (
                resident_match.group(1)
            )

        # -------------------------------------------------
        # FILE SOURCE
        # -------------------------------------------------

        from_match = re.search(
            r'FROM\s+[\'"](.+?)[\'"]',
            block,
            flags=re.IGNORECASE
        )

        if from_match:

            source_type = (
                SourceType.FILE
            )

            source_table = (
                from_match.group(1)
            )

        # -------------------------------------------------
        # Return model
        # -------------------------------------------------

        return QVSLoad(
            table_name=table_name,
            fields=fields,
            source_type=source_type,
            source_table=source_table,
            sql_query=sql_query
        )