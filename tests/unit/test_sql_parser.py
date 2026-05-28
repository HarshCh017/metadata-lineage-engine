from lineage_platform.parsers.qlikview.sql_parser import SQLParser


def test_simple_sql():
    sql = "SELECT ID, Name FROM PROD.USERS;"
    tables, columns, partial = SQLParser.extract_sql_tables(sql)
    assert tables == ["USERS"]
    assert columns["ID"] == "ID"
    assert columns["Name"] == "Name"
    assert partial is False


def test_aliased_columns():
    sql = "SELECT u.ID AS UserID, Name FROM PROD.USERS u;"
    tables, columns, partial = SQLParser.extract_sql_tables(sql)
    assert tables == ["USERS"]
    assert columns["UserID"] == "ID"
    assert columns["Name"] == "Name"


def test_lineage_partial():
    sql = "SELECT * FROM $(vTable);"
    tables, columns, partial = SQLParser.extract_sql_tables(sql)
    assert partial is True


def test_dialect_injection():
    # Example using dialect specific parsing if it fails normally, or just showing it accepts dialect
    sql = "SELECT TOP 10 * FROM PROD.USERS;"
    # SQLGlot will parse this differently depending on dialect, but we just want to ensure no crash
    tables, columns, partial = SQLParser.extract_sql_tables(sql, dialect="teradata")
    assert tables == ["USERS"]
