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
            session.run("MATCH (n) DETACH DELETE n") # clean state
            yield session
            session.run("MATCH (n) DETACH DELETE n")
        driver.close()
    except Exception:
        pytest.skip("Neo4j not running on localhost:7687")

def test_graph_writer_idempotency(neo4j_session):
    app = QlikViewApp(app_name="TestApp")
    load = QVSLoad(
        table_name="Users",
        fields=["ID", "Name"],
        source_type=SourceType.SQL,
        source_table="PROD.USERS"
    )
    app.loads.append(load)
    
    writer = GraphWriter()
    
    # Write first time
    writer.write_app(app)
    
    result = neo4j_session.run("MATCH (n) RETURN count(n) as count")
    node_count_1 = result.single()["count"]
    
    # Write second time
    writer.write_app(app)
    
    result = neo4j_session.run("MATCH (n) RETURN count(n) as count")
    node_count_2 = result.single()["count"]
    
    assert node_count_1 > 0
    assert node_count_1 == node_count_2, "Node count changed after second write - not idempotent!"
