import sqlglot
from sqlglot import exp


class SQLParser:
    """
    SQL lineage extraction using sqlglot.

    Responsibilities:
    - Normalize Qlik SQL syntax
    - Parse SQL queries safely
    - Extract source tables
    - Filter invalid lineage tokens
    """

    # =====================================================
    # INVALID TABLE NAMES
    # =====================================================

    INVALID_TABLE_NAMES = {
        # Qlik keywords
        "load",
        "resident",
        "join",
        "left",
        "right",
        "inner",
        "outer",
        "full",
        # SQL keywords
        "select",
        "from",
        "where",
        "group",
        "by",
        "order",
        "having",
        "union",
        # Misc
        "sql",
        "null",
    }

    # =====================================================
    # SQL NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize_sql(sql_query: str) -> str:
        """
        Convert Qlik SQL syntax into valid SQLGlot syntax.
        """

        if not sql_query:
            return ""

        # ----------------------------------------------
        # Remove Qlik prefix
        # ----------------------------------------------

        sql_query = sql_query.replace("SQL SELECT", "SELECT")

        sql_query = sql_query.replace("sql select", "SELECT")

        # ----------------------------------------------
        # Remove trailing semicolon
        # ----------------------------------------------

        sql_query = sql_query.rstrip(";")

        # ----------------------------------------------
        # Normalize whitespace
        # ----------------------------------------------

        sql_query = " ".join(sql_query.split())

        return sql_query

    # =====================================================
    # VALIDATION
    # =====================================================

    @staticmethod
    def is_valid_table_name(table_name: str) -> bool:
        """
        Validate extracted lineage table names.
        """

        if not table_name:
            return False

        table_name = table_name.strip()

        if not table_name:
            return False

        # ----------------------------------------------
        # Ignore tiny tokens
        # ----------------------------------------------

        if len(table_name) <= 2:
            return False

        # ----------------------------------------------
        # Ignore keywords
        # ----------------------------------------------

        if table_name.lower() in SQLParser.INVALID_TABLE_NAMES:
            return False

        return True

    # =====================================================
    # MAIN TABLE EXTRACTION
    # =====================================================

    @staticmethod
    def extract_sql_tables(sql_query: str):

        tables = []

        try:

            # ------------------------------------------
            # Normalize SQL
            # ------------------------------------------

            sql_query = SQLParser.normalize_sql(sql_query)

            if not sql_query:
                return []

            # ------------------------------------------
            # Parse SQL
            # ------------------------------------------

            parsed = sqlglot.parse_one(sql_query)

            # ------------------------------------------
            # Extract table references
            # ------------------------------------------

            for table in parsed.find_all(exp.Table):

                table_name = table.name.strip()

                # --------------------------------------
                # Validation
                # --------------------------------------

                if not SQLParser.is_valid_table_name(table_name):
                    continue

                tables.append(table_name)

        except Exception as e:

            print(f"SQL parsing failed: {e}")

        # ------------------------------------------------
        # Remove duplicates while preserving order
        # ------------------------------------------------

        unique_tables = []

        seen = set()

        for table in tables:

            if table not in seen:

                unique_tables.append(table)

                seen.add(table)

        return unique_tables
