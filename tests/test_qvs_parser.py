from lineage_platform.parsers.qlikview.qvs_parser import QVSParser


def test_enterprise_qvs_parsing():
    parser = QVSParser()
    app = parser.parse("data/input/qlikview/99_enterprise_lineage_test.qvs")
    assert app is not None
    assert len(app.loads) >= 10
    assert len(app.joins) >= 4
    assert len(app.fields) >= 10
