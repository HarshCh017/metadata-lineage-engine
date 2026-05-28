import structlog
from typing import Optional, Dict, Any, List
from lineage_platform.neo4j.repository import LineageRepository
from lineage_platform.models.snapshot import SnapshotContext

logger = structlog.get_logger()

class GraphService:
    """
    Business layer for graph query semantics.
    Abstracts the LineageRepository logic away from APIs and MCP.
    """
    
    def __init__(self, repository: Optional[LineageRepository] = None):
        self.repo = repository or LineageRepository()

    def search_tables(self, query: str, snapshot: Optional[SnapshotContext] = None) -> str:
        try:
            result = self.repo.search_tables(query, snapshot)
            tables = [f"Name: {r['name']}, FQN: {r['fqn']}" for r in result]
            if not tables:
                return f"No tables found matching '{query}'."
            return "Found tables:\\n" + "\\n".join(tables)
        except Exception as e:
            logger.error("graph_service_search_error", error=str(e))
            return f"Error executing search: {str(e)}"

    def get_table_lineage(self, table_fqn: str, depth: int = 3, snapshot: Optional[SnapshotContext] = None) -> str:
        try:
            result = self.repo.get_table_lineage(table_fqn, depth=depth, snapshot=snapshot)
            lineage = []
            for r in result:
                lineage.append(f"[{r['dist']} hops] {r['upstream_fqn']} -> {r['target_fqn']}")
            
            if not lineage:
                return f"No upstream lineage found for '{table_fqn}' within depth {depth}."
            return f"Lineage for {table_fqn}:\\n" + "\\n".join(lineage)
        except Exception as e:
            logger.error("graph_service_lineage_error", error=str(e))
            return f"Error fetching lineage: {str(e)}"

    def get_dashboard_metrics(self, dashboard_name: str, snapshot: Optional[SnapshotContext] = None) -> str:
        try:
            result = self.repo.get_dashboard_metrics(dashboard_name, snapshot)
            metrics = []
            for r in result:
                fields_str = ", ".join(r['fields'])
                metrics.append(f"Sheet: {r['sheet']} | Chart: {r['chart']} | Fields: {fields_str}")
            
            if not metrics:
                return f"No metrics/charts found for dashboard containing '{dashboard_name}'."
            return "Dashboard Metrics:\\n" + "\\n".join(metrics)
        except Exception as e:
            logger.error("graph_service_dashboard_error", error=str(e))
            return f"Error fetching metrics: {str(e)}"

    def get_script_subroutines(self, script_name: str, snapshot: Optional[SnapshotContext] = None) -> str:
        try:
            result = self.repo.get_script_subroutines(script_name, snapshot)
            subs = []
            for r in result:
                subs.append(f"Script: {r['script']} | Subroutine: {r['subroutine']}")
            
            if not subs:
                return f"No subroutines found for script containing '{script_name}'."
            return "Script Subroutines:\\n" + "\\n".join(subs)
        except Exception as e:
            logger.error("graph_service_script_error", error=str(e))
            return f"Error fetching subroutines: {str(e)}"
            
    def close(self):
        self.repo.close()
