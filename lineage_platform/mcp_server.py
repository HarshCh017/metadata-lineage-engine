from mcp.server.fastmcp import FastMCP
import structlog
from lineage_platform.api.services.graph_service import GraphService
from lineage_platform.models.snapshot import SnapshotContext
from typing import Optional

logger = structlog.get_logger()

# Initialize FastMCP Server
mcp = FastMCP("Metadata Lineage Engine")


def get_service():
    return GraphService()


@mcp.tool()
def search_tables(query: str, as_of_timestamp: Optional[str] = None, snapshot_id: Optional[str] = None) -> str:
    """
    Search for tables in the metadata graph matching a query string.
    Optionally provide as_of_timestamp to query historical lineage state.
    """
    svc = get_service()
    try:
        snapshot = SnapshotContext(as_of_timestamp=as_of_timestamp, snapshot_id=snapshot_id)
        return svc.search_tables(query, snapshot=snapshot)
    finally:
        svc.close()


@mcp.tool()
def get_table_lineage(table_fqn: str, depth: int = 3, as_of_timestamp: Optional[str] = None, snapshot_id: Optional[str] = None) -> str:
    """
    Retrieve the upstream lineage for a specific table using its Fully Qualified Name (FQN).
    Optionally provide as_of_timestamp to query historical lineage state.
    """
    svc = get_service()
    try:
        snapshot = SnapshotContext(as_of_timestamp=as_of_timestamp, snapshot_id=snapshot_id)
        return svc.get_table_lineage(table_fqn, depth=depth, snapshot=snapshot)
    finally:
        svc.close()


@mcp.tool()
def get_dashboard_metrics(dashboard_name: str, as_of_timestamp: Optional[str] = None, snapshot_id: Optional[str] = None) -> str:
    """
    Get the charts and the physical fields used by a specific Qlik Dashboard/Sheet.
    """
    svc = get_service()
    try:
        snapshot = SnapshotContext(as_of_timestamp=as_of_timestamp, snapshot_id=snapshot_id)
        return svc.get_dashboard_metrics(dashboard_name, snapshot=snapshot)
    finally:
        svc.close()


@mcp.tool()
def get_script_subroutines(script_name: str, as_of_timestamp: Optional[str] = None, snapshot_id: Optional[str] = None) -> str:
    """
    Get the subroutines defined within a specific Qlik script.
    """
    svc = get_service()
    try:
        snapshot = SnapshotContext(as_of_timestamp=as_of_timestamp, snapshot_id=snapshot_id)
        return svc.get_script_subroutines(script_name, snapshot=snapshot)
    finally:
        svc.close()


if __name__ == "__main__":
    # Start the MCP server using standard I/O (required for Claude Desktop integration)
    mcp.run()
