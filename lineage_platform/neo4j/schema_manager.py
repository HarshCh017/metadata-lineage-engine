import os
from neo4j import GraphDatabase
import structlog

logger = structlog.get_logger()

CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (q:QlikScript) REQUIRE q.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (t:QlikTable) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Connection) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Table) REQUIRE t.fully_qualified_name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Attribute) REQUIRE a.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR (c:QlikChart) ON (c.name)",
    "CREATE INDEX IF NOT EXISTS FOR (t:Table) ON (t.name)",
    "CREATE INDEX IF NOT EXISTS FOR (v:Variable) ON (v.name)",
]


def ensure_constraints():
    """
    Create all required Neo4j constraints and indexes.
    Should be called once at application startup.
    """
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session() as session:
            for stmt in CONSTRAINTS:
                try:
                    session.run(stmt)
                    logger.info("constraint_created", statement=stmt)
                except Exception as e:
                    logger.warning("constraint_skip", statement=stmt, reason=str(e))

            for stmt in INDEXES:
                try:
                    session.run(stmt)
                    logger.info("index_created", statement=stmt)
                except Exception as e:
                    logger.warning("index_skip", statement=stmt, reason=str(e))
    finally:
        driver.close()
