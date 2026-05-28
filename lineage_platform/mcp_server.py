from mcp.server.fastmcp import FastMCP
import structlog
from lineage_platform.neo4j.repository import LineageRepository

logger = structlog.get_logger()

# Initialize FastMCP Server
mcp = FastMCP("Metadata Lineage Engine")

# Dependency: LineageRepository
def get_repo():
    return LineageRepository()

@mcp.tool()
def search_tables(query: str) -> str:
    """
    Search for tables in the metadata graph matching a query string.
    Returns a list of matching table names and their IDs.
    """
    repo = get_repo()
    try:
        result = repo.search_tables(query)
        tables = [f"Name: {r['name']}, FQN: {r['fqn']}" for r in result]
        if not tables:
            return f"No tables found matching '{query}'."
        return "Found tables:\\n" + "\\n".join(tables)
    except Exception as e:
        return f"Error executing search: {str(e)}"
    finally:
        repo.close()

@mcp.tool()
def get_table_lineage(table_fqn: str, depth: int = 3) -> str:
    """
    Retrieve the upstream lineage for a specific table using its Fully Qualified Name (FQN).
    Shows which tables feed into this table.
    """
    repo = get_repo()
    try:
        result = repo.get_table_lineage(table_fqn, depth=depth)
        lineage = []
        for r in result:
            lineage.append(f"[{r['dist']} hops] {r['upstream_fqn']} -> {r['target_fqn']}")
        
        if not lineage:
            return f"No upstream lineage found for '{table_fqn}' within depth {depth}."
        return f"Lineage for {table_fqn}:\\n" + "\\n".join(lineage)
    except Exception as e:
        return f"Error fetching lineage: {str(e)}"
    finally:
        repo.close()

@mcp.tool()
def get_dashboard_metrics(dashboard_name: str) -> str:
    """
    Get the charts and the physical fields used by a specific Qlik Dashboard/Sheet.
    """
    repo = get_repo()
    try:
        result = repo.get_dashboard_metrics(dashboard_name)
        metrics = []
        for r in result:
            fields_str = ", ".join(r['fields'])
            metrics.append(f"Sheet: {r['sheet']} | Chart: {r['chart']} | Fields: {fields_str}")
        
        if not metrics:
            return f"No metrics/charts found for dashboard containing '{dashboard_name}'."
        return "Dashboard Metrics:\\n" + "\\n".join(metrics)
    except Exception as e:
        return f"Error fetching metrics: {str(e)}"
    finally:
        repo.close()

@mcp.tool()
def get_script_subroutines(script_name: str) -> str:
    """
    Get the subroutines defined within a specific Qlik script.
    Allows Claude to understand the modular logic transformations.
    """
    repo = get_repo()
    try:
        result = repo.get_script_subroutines(script_name)
        subs = []
        for r in result:
            subs.append(f"Script: {r['script']} | Subroutine: {r['subroutine']}")
        
        if not subs:
            return f"No subroutines found for script containing '{script_name}'."
        return "Script Subroutines:\\n" + "\\n".join(subs)
    except Exception as e:
        return f"Error fetching subroutines: {str(e)}"
    finally:
        repo.close()

if __name__ == "__main__":
    # Start the MCP server using standard I/O (required for Claude Desktop integration)
    mcp.run()
