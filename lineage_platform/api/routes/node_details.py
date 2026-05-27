from fastapi import APIRouter
from neo4j import GraphDatabase
import os

router = APIRouter()

# =========================================================
# Neo4j Driver
# =========================================================

driver = GraphDatabase.driver(

    os.getenv(
        "NEO4J_URI",
        "bolt://localhost:7687"
    ),

    auth=(

        os.getenv(
            "NEO4J_USERNAME",
            "neo4j"
        ),

        os.getenv(
            "NEO4J_PASSWORD",
            "password"
        )
    )
)

# =========================================================
# Node Metadata Endpoint
# =========================================================

@router.get("/node/{node_id}")
def get_node_details(node_id: str):

    query = """
    MATCH (n)
    WHERE n.id = $node_id

    OPTIONAL MATCH (n)-[r]-(m)

    RETURN
        n,
        labels(n) AS labels,

        collect(
            DISTINCT {
                relationship: type(r),
                connected_node: m.name,
                connected_labels: labels(m)
            }
        ) AS connections
    """

    with driver.session() as session:

        result = session.run(
            query,
            node_id=node_id
        )

        record = result.single()

        # -------------------------------------------------
        # Node not found
        # -------------------------------------------------

        if not record or record["n"] is None:

            return {
                "error": "Node not found"
            }

        # -------------------------------------------------
        # Convert Neo4j node to dict
        # -------------------------------------------------

        node_data = dict(
            record["n"]
        )

        # -------------------------------------------------
        # Build response
        # -------------------------------------------------

        return {

            "labels": record["labels"],

            "properties": node_data,

            "connections": record[
                "connections"
            ]
        }

# =========================================================
# Health Test Endpoint
# =========================================================

@router.get("/node-test")
def node_test():

    return {
        "status": "node metadata route working"
    }