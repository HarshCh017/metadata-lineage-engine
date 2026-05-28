from lineage_platform.parsers.qlikview.qvs_parser import QVSParser


def test_end_to_end():
    parser = QVSParser()
    app = parser.parse("tests/fixtures/qvs/sample.qvs")
    assert app.loads is not None
