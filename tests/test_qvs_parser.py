import pytest
from lineage_platform.parsers.qlikview.qvs_parser import QVSParser

def test_enterprise_qvs_parsing():
    parser = QVSParser()
    app = parser.parse('chaos_test.qvs')
    assert app is not None
    # Chaos test has exactly 5 tables
    assert len(app.tables) == 5