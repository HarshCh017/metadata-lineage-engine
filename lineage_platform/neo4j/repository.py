import os
from typing import List, Dict, Any
from neo4j import GraphDatabase, READ_ACCESS
import structlog

logger = structlog.get_logger()

class LineageRepository:
    """
    Data Access Layer (DAL) for the Lineage Engine.
    Abstracts raw Cypher and enforces temporal governance rules (e.g. is_active = true)
    automatically so that callers (like MCP AI) don't have to remember them.
    """
    def __init__(self):
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def _execute_read(self, cypher: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        parameters = parameters or {}
        try:
            with self.driver.session(default_access_mode=READ_ACCESS) as session:
                result = session.run(cypher, parameters, timeout=5000)
                return [dict(r) for r in result]
        except Exception as e:
            logger.error("repository_read_error", error=str(e), cypher=cypher)
            raise e

    def search_tables(self, query: str) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (t:Table)
        WHERE (toLower(t.name) CONTAINS toLower($query) 
           OR toLower(t.fully_qualified_name) CONTAINS toLower($query))
          AND coalesce(t.is_active, true) = true
        RETURN t.name AS name, t.fully_qualified_name AS fqn
        LIMIT 20
        """
        return self._execute_read(cypher, {"query": query})

    def get_table_lineage(self, table_fqn: str, depth: int = 3) -> List[Dict[str, Any]]:
        # Enforce is_active at the relationship level
        cypher = """
        MATCH p = (upstream:Table)-[r:DERIVES_FROM|LOADS_FROM_TABLE*1..$depth]->(target:Table {fully_qualified_name: $fqn})
        WHERE all(rel IN relationships(p) WHERE coalesce(rel.is_active, true) = true)
          AND coalesce(upstream.is_active, true) = true
          AND coalesce(target.is_active, true) = true
        RETURN upstream.fully_qualified_name AS upstream_fqn, 
               target.fully_qualified_name AS target_fqn,
               length(p) AS dist
        ORDER BY dist ASC
        LIMIT 50
        """
        return self._execute_read(cypher, {"fqn": table_fqn, "depth": depth})

    def get_dashboard_metrics(self, dashboard_name: str) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (s:QlikSheet)-[r1:DISPLAYS_CHART]->(c:QlikChart)-[r2:USES_FIELD]->(f:Attribute)
        WHERE toLower(s.name) CONTAINS toLower($name)
          AND coalesce(r1.is_active, true) = true
          AND coalesce(r2.is_active, true) = true
          AND coalesce(s.is_active, true) = true
        RETURN s.name AS sheet, c.title AS chart, collect(f.name) AS fields
        LIMIT 50
        """
        return self._execute_read(cypher, {"name": dashboard_name})

    def get_script_subroutines(self, script_name: str) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (s:QlikScript)-[r:DEFINES_SUBROUTINE]->(sub:Subroutine)
        WHERE toLower(s.name) CONTAINS toLower($name)
          AND coalesce(r.is_active, true) = true
          AND coalesce(s.is_active, true) = true
        RETURN s.name AS script, sub.name AS subroutine
        LIMIT 50
        """
        return self._execute_read(cypher, {"name": script_name})

    def close(self):
        self.driver.close()
