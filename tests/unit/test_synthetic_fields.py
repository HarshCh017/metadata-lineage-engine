import pytest
from lineage_platform.parsers.qlikview.qvs_parser import QVSParser

def test_synthetic_fields():
    parser = QVSParser()
    app = parser.parse('tests/fixtures/qvs/sample.qvs')
    # Just verify we can iterate fields without crashing
    for table in app.tables:
        for field in table.fields:
            assert field.name is not None