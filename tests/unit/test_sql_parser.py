from lineage_platform.parsers.qlikview.sql_parser import SQLParser


def test_sql_table_extraction():

    sql = """
    SELECT *
    FROM PROD.SALES.CUSTOMER
    """

    tables = SQLParser.extract_sql_tables(sql)

    assert len(tables) > 0

    assert "CUSTOMER" in [table.upper().split(".")[-1] for table in tables]
