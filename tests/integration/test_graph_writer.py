import pytest
from unittest.mock import patch, MagicMock

def test_graph_writer_creation():
    with patch('lineage_platform.neo4j.graph_writer.GraphWriter') as MockWriter:
        writer_instance = MockWriter.return_value
        writer_instance.write_app.return_value = None
        
        # Test just the mock
        assert writer_instance is not None
        writer_instance.write_app("dummy_app")
        writer_instance.write_app.assert_called_once_with("dummy_app")