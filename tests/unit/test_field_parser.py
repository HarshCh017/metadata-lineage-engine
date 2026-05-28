import pytest
from lineage_platform.parsers.qlikview.field_parser import FieldParser

def test_simple_fields():
    block = "LOAD A, B, C;"
    fields = FieldParser.extract_fields(block)
    assert fields == ["A", "B", "C"]

def test_alias_fields():
    block = "LOAD A AS Alpha, B AS Beta;"
    fields = FieldParser.extract_fields(block)
    assert fields == ["Alpha", "Beta"]

def test_nested_functions():
    # Comma inside parentheses should not split the field
    block = "LOAD SUM(A, B) AS Total, C;"
    fields = FieldParser.extract_fields(block)
    assert fields == ["Total", "C"]

def test_apply_map():
    block = "LOAD ApplyMap('MapName', SourceID), B;"
    fields = FieldParser.extract_fields(block)
    assert fields == ["SourceID", "B"]

def test_apply_map_with_alias():
    block = "LOAD ApplyMap('MapName', SourceID) AS MappedID, B;"
    fields = FieldParser.extract_fields(block)
    assert fields == ["MappedID", "B"]

def test_star_load():
    block = "LOAD *;"
    fields = FieldParser.extract_fields(block)
    assert fields == ["*"]
