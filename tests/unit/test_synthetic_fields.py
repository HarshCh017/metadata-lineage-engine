from lineage_platform.parsers.qlikview.field_parser import FieldParser


def test_synthetic_fields():
    script = "LOAD SUM(Amount) / Rate AS SyntheticField, B;"
    fields = FieldParser.extract_fields(script)
    assert fields == ["SyntheticField", "B"]
