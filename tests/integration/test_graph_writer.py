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

    writer.write_app(app)

    assert writer is not None

    writer.close()