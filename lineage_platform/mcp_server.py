import os
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase
import structlog

logger = structlog.get_logger()

# Initialize FastMCP Server
mcp = FastMCP("Metadata Lineage Engine")

# Dependency: Neo4j Driver
def get_driver():
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))

@mcp.tool()
def search_tables(query: str) -> str:
    """
    Search for tables in the metadata graph matching a query string.
    Returns a list of matching table names and their IDs.
    """
    driver = get_driver()
    cypher = \"\"\"
    MATCH (t:Table)
    WHERE toLower(t.name) CONTAINS toLower($query) OR toLower(t.fully_qualified_name) CONTAINS toLower($query)
    RETURN t.name AS name, t.fully_qualified_name AS fqn
    LIMIT 20
    \"\"\"
    try:
        with driver.session() as session:
            result = session.run(cypher, query=query)
            tables = [f"Name: {r['name']}, FQN: {r['fqn']}" for r in result]
            if not tables:
                return f"No tables found matching '{query}'."
            return "Found tables:\\n" + "\\n".join(tables)
    except Exception as e:
        return f"Error executing search: {str(e)}"
    finally:
        driver.close()

@mcp.tool()
def get_table_lineage(table_fqn: str, depth: int = 3) -> str:
    """
    Retrieve the upstream lineage for a specific table using its Fully Qualified Name (FQN).
    Shows which tables feed into this table.
    """
    driver = get_driver()
    cypher = \"\"\"
    MATCH p = (upstream:Table)-[:DERIVES_FROM|LOADS_FROM_TABLE*1..$depth]->(target:Table {fully_qualified_name: $fqn})
    RETURN upstream.fully_qualified_name AS upstream_fqn, 
           target.fully_qualified_name AS target_fqn,
           length(p) AS dist
    ORDER BY dist ASC
    LIMIT 50
    \"\"\"
    try:
        with driver.session() as session:
            result = session.run(cypher, fqn=table_fqn, depth=depth)
            lineage = []
            for r in result:
                lineage.append(f"[{r['dist']} hops] {r['upstream_fqn']} -> {r['target_fqn']}")
            
            if not lineage:
                return f"No upstream lineage found for '{table_fqn}' within depth {depth}."
            return f"Lineage for {table_fqn}:\\n" + "\\n".join(lineage)
    except Exception as e:
        return f"Error fetching lineage: {str(e)}"
    finally:
        driver.close()

@mcp.tool()
def get_dashboard_metrics(dashboard_name: str) -> str:
    """
    Get the charts and the physical fields used by a specific Qlik Dashboard/Sheet.
    """
    driver = get_driver()
    cypher = \"\"\"
    MATCH (s:QlikSheet)-[:DISPLAYS_CHART]->(c:QlikChart)-[:USES_FIELD]->(f:Attribute)
    WHERE toLower(s.name) CONTAINS toLower($name)
    RETURN s.name AS sheet, c.title AS chart, collect(f.name) AS fields
    LIMIT 50
    \"\"\"
    try:
        with driver.session() as session:
            result = session.run(cypher, name=dashboard_name)
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
        driver.close()

@mcp.tool()
def get_script_subroutines(script_name: str) -> str:
    """
    Get the subroutines defined within a specific Qlik script.
    Allows Claude to understand the modular logic transformations.
    """
    driver = get_driver()
    cypher = \"\"\"
    MATCH (s:QlikScript)-[:DEFINES_SUBROUTINE]->(sub:Subroutine)
    WHERE toLower(s.name) CONTAINS toLower($name)
    RETURN s.name AS script, sub.name AS subroutine
    LIMIT 50
    \"\"\"
    try:
        with driver.session() as session:
            result = session.run(cypher, name=script_name)
            subs = []
            for r in result:
                subs.append(f"Script: {r['script']} | Subroutine: {r['subroutine']}")
            
            if not subs:
                return f"No subroutines found for script containing '{script_name}'."
            return "Script Subroutines:\\n" + "\\n".join(subs)
    except Exception as e:
        return f"Error fetching subroutines: {str(e)}"
    finally:
        driver.close()

if __name__ == "__main__":
    # Start the MCP server using standard I/O (required for Claude Desktop integration)
    mcp.run()
