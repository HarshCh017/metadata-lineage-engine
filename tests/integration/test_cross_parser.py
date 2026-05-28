import os
import pytest
from neo4j import GraphDatabase
from lineage_platform.neo4j.graph_writer import GraphWriter
from lineage_platform.models.qlik_models import QlikViewApp, QVSLoad, SourceType

@pytest.fixture
def neo4j_session():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            yield session
            session.run("MATCH (n) DETACH DELETE n")
        driver.close()
    except Exception:
        pytest.skip("Neo4j not running on localhost:7687")

def test_cross_parser_merge(neo4j_session):
    # Preload a Table node that a Tableau parser might have written
    fqn = "UNKNOWN.UNKNOWN.PROD.USERS"
    neo4j_session.run(
        """
        MERGE (s:Table {name: 'PROD.USERS'})
        SET s.fully_qualified_name = $fqn
        """,
        fqn=fqn
    )
    
    result = neo4j_session.run("MATCH (t:Table {name: 'PROD.USERS'}) RETURN count(t) as count")
    assert result.single()["count"] == 1
    
    app = QlikViewApp(app_name="TestApp")
    load = QVSLoad(
        table_name="Users",
        fields=["ID", "Name"],
        source_type=SourceType.SQL,
        source_table="PROD.USERS"
    )
    app.loads.append(load)
    
    writer = GraphWriter()
    writer.write_app(app)
    
    # Verify no duplicate Table nodes were created
    result = neo4j_session.run("MATCH (t:Table {name: 'PROD.USERS'}) RETURN count(t) as count")
    node_count = result.single()["count"]
    
    assert node_count == 1, "Duplicate Table node created, fully_qualified_name merge failed!"
