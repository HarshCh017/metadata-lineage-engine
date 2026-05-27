from lineage_platform.parsers.qlikview.field_parser import FieldParser


def test_field_parsing():

    block = """
    LOAD
        CustomerID,
        UPPER(Name) AS Name_Upper,
        SUM(Sales) AS TotalSales
    FROM table;
    """

    fields = FieldParser.extract_fields(block)

    assert 'CustomerID' in fields
    assert 'Name_Upper' in fields
    assert 'TotalSales' in fields