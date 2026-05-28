import re
from typing import List

from lineage_platform.models.qlik_models import QVSConnection


class ConnectionParser:
    """
    Extracts QlikView connection metadata.

    Supports LIB, ODBC, OLEDB, and CUSTOM connection types.
    Parses connection class, server, database name, and infers database type.
    """

    CONNECTION_PATTERN = re.compile(
        r"(?P<conn_class>LIB|ODBC|OLEDB|CUSTOM)\s+CONNECT\s+TO\s+['\"\[]?(?P<conn_str>[^'\"\];]+)['\"\]]?",
        re.IGNORECASE,
    )

    @classmethod
    def extract_connections(cls, content: str) -> List[QVSConnection]:

        connections = []

        matches = cls.CONNECTION_PATTERN.finditer(content)

        for match in matches:

            conn_class = match.group("conn_class").upper()
            raw_string = match.group("conn_str").strip()

            # Parse server and database from connection string
            server = cls._extract_field(raw_string, ["SERVER", "HOST", "Data Source", "DSN"])
            database_name = cls._extract_field(raw_string, ["DATABASE", "DBQ", "Initial Catalog"])
            db_type = cls._infer_database_type(conn_class, raw_string)

            connections.append(
                QVSConnection(
                    connection_name=raw_string.split(";")[0].strip() if ";" in raw_string else raw_string,
                    connection_string=raw_string,
                    database_type=db_type,
                    connection_class=conn_class,
                    server=server,
                    database_name=database_name,
                )
            )

        return connections

    @staticmethod
    def _extract_field(conn_str: str, keys: List[str]) -> str:
        """Extract a named field from a connection string like 'SERVER=host;DATABASE=db'."""
        for key in keys:
            pattern = re.compile(rf"{re.escape(key)}\s*=\s*([^;]+)", re.IGNORECASE)
            m = pattern.search(conn_str)
            if m:
                return m.group(1).strip()
        return ""

    @staticmethod
    def _infer_database_type(conn_class: str, conn_str: str) -> str:
        """Infer database vendor from connection class and string keywords."""
        lower = conn_str.lower()
        if "teradata" in lower:
            return "TERADATA"
        elif "oracle" in lower:
            return "ORACLE"
        elif "postgres" in lower or "pgsql" in lower:
            return "POSTGRESQL"
        elif "mysql" in lower:
            return "MYSQL"
        elif "sqlserver" in lower or "mssql" in lower or "sql server" in lower:
            return "SQLSERVER"
        elif conn_class == "OLEDB":
            return "OLEDB"
        elif conn_class == "ODBC":
            return "ODBC"
        elif conn_class == "LIB":
            return "LIB"
        return "UNKNOWN"
