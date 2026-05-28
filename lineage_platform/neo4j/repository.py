import os
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, READ_ACCESS
import structlog
from lineage_platform.models.snapshot import SnapshotContext

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

    def _inject_temporal_predicate(self, snapshot: Optional[SnapshotContext], entity_alias: str) -> str:
        """
        Automatically injects governance-grade temporal predicates.
        """
        if snapshot and snapshot.as_of_timestamp:
            return f"({entity_alias}.valid_from <= $as_of_timestamp AND ({entity_alias}.valid_to > $as_of_timestamp OR {entity_alias}.valid_to IS NULL))"
        return f"coalesce({entity_alias}.is_active, true) = true"

    def search_tables(self, query: str, snapshot: Optional[SnapshotContext] = None) -> List[Dict[str, Any]]:
        temp_predicate = self._inject_temporal_predicate(snapshot, "t")
        cypher = f"""
        MATCH (t:Table)
        WHERE (toLower(t.name) CONTAINS toLower($query) 
           OR toLower(t.fully_qualified_name) CONTAINS toLower($query))
          AND {temp_predicate}
        RETURN t.name AS name, t.fully_qualified_name AS fqn
        LIMIT 20
        """
        params = {"query": query}
        if snapshot and snapshot.as_of_timestamp:
            params["as_of_timestamp"] = snapshot.as_of_timestamp
        return self._execute_read(cypher, params)

    def get_table_lineage(self, table_fqn: str, depth: int = 3, snapshot: Optional[SnapshotContext] = None) -> List[Dict[str, Any]]:
        r_pred = self._inject_temporal_predicate(snapshot, "rel")
        u_pred = self._inject_temporal_predicate(snapshot, "upstream")
        t_pred = self._inject_temporal_predicate(snapshot, "target")
        
        cypher = f"""
        MATCH p = (upstream:Table)-[r:DERIVES_FROM|LOADS_FROM_TABLE*1..$depth]->(target:Table {{fully_qualified_name: $fqn}})
        WHERE all(rel IN relationships(p) WHERE {r_pred})
          AND {u_pred}
          AND {t_pred}
        RETURN upstream.fully_qualified_name AS upstream_fqn, 
               target.fully_qualified_name AS target_fqn,
               length(p) AS dist
        ORDER BY dist ASC
        LIMIT 50
        """
        params = {"fqn": table_fqn, "depth": depth}
        if snapshot and snapshot.as_of_timestamp:
            params["as_of_timestamp"] = snapshot.as_of_timestamp
        return self._execute_read(cypher, params)

    def get_dashboard_metrics(self, dashboard_name: str, snapshot: Optional[SnapshotContext] = None) -> List[Dict[str, Any]]:
        r1_pred = self._inject_temporal_predicate(snapshot, "r1")
        r2_pred = self._inject_temporal_predicate(snapshot, "r2")
        s_pred = self._inject_temporal_predicate(snapshot, "s")
        
        cypher = f"""
        MATCH (s:QlikSheet)-[r1:DISPLAYS_CHART]->(c:QlikChart)-[r2:USES_FIELD]->(f:Attribute)
        WHERE toLower(s.name) CONTAINS toLower($name)
          AND {r1_pred}
          AND {r2_pred}
          AND {s_pred}
        RETURN s.name AS sheet, c.title AS chart, collect(f.name) AS fields
        LIMIT 50
        """
        params = {"name": dashboard_name}
        if snapshot and snapshot.as_of_timestamp:
            params["as_of_timestamp"] = snapshot.as_of_timestamp
        return self._execute_read(cypher, params)

    def get_script_subroutines(self, script_name: str, snapshot: Optional[SnapshotContext] = None) -> List[Dict[str, Any]]:
        r_pred = self._inject_temporal_predicate(snapshot, "r")
        s_pred = self._inject_temporal_predicate(snapshot, "s")
        cypher = f"""
        MATCH (s:QlikScript)-[r:DEFINES_SUBROUTINE]->(sub:Subroutine)
        WHERE toLower(s.name) CONTAINS toLower($name)
          AND {r_pred}
          AND {s_pred}
        RETURN s.name AS script, sub.name AS subroutine
        LIMIT 50
        """
        params = {"name": script_name}
        if snapshot and snapshot.as_of_timestamp:
            params["as_of_timestamp"] = snapshot.as_of_timestamp
        return self._execute_read(cypher, params)

    def close(self):
        self.driver.close()
