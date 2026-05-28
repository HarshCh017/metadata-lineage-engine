import pytest
from lineage_platform.parsers.qlikview.qvs_parser import QVSParser

def test_end_to_end():
    parser = QVSParser()
    app = parser.parse('tests/fixtures/qvs/sample.qvs')
    assert app is not None
    assert app.tables is not None
    assert len(app.tables) > 0