import pytest

from neo4j.exceptions import ServiceUnavailable

from lineage_platform.parsers.qlikview.qvs_parser import (
    QVSParser
)

from lineage_platform.neo4j.graph_writer import (
    GraphWriter
)


def test_graph_writer_creation():

    parser = QVSParser()

    app = parser.parse(
        'tests/fixtures/qvs/sample.qvs'
    )

    writer = GraphWriter()

    try:

        writer.write_app(app)

        assert writer is not None

    except ServiceUnavailable:

        pytest.skip(
            "Neo4j database not available"
        )

    finally:

        writer.close()