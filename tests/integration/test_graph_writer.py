import pytest
from lineage_platform.parsers.qlikview.qvs_parser import QVSParser
from lineage_platform.graph.batch_graph_writer import BatchGraphWriter

def test_graph_writer_creation():
    parser = QVSParser()
    app = parser.parse('tests/fixtures/qvs/sample.qvs')
    
    # We won't actually write to Neo4j in CI to prevent database dependency,
    # but we can assert the writer initializes correctly and has the methods
    writer = BatchGraphWriter("bolt://localhost:7687", "neo4j", "password")
    assert writer is not None
    assert hasattr(writer, 'write_batch')
    assert hasattr(writer, 'setup_indexes_and_constraints')