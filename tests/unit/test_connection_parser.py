from lineage_platform.parsers.qlikview.connection_parser import ConnectionParser


def test_lib_connect():
    script = "LIB CONNECT TO 'MyDatabase';"
    conns = ConnectionParser.extract_connections(script)
    assert len(conns) == 1
    assert conns[0].connection_name == "MyDatabase"


def test_odbc_connect():
    script = 'ODBC CONNECT TO "OracleDB";'
    conns = ConnectionParser.extract_connections(script)
    assert len(conns) == 1
    assert conns[0].connection_name == "OracleDB"


def test_oledb_connect():
    script = "OLEDB CONNECT TO [SQLServer];"
    conns = ConnectionParser.extract_connections(script)
    assert len(conns) == 1
    assert conns[0].connection_name == "SQLServer"


def test_multiple_connections():
    script = """
    LIB CONNECT TO 'FirstDB';
    ODBC CONNECT TO 'SecondDB';
    """
    conns = ConnectionParser.extract_connections(script)
    assert len(conns) == 2
    assert conns[0].connection_name == "FirstDB"
    assert conns[1].connection_name == "SecondDB"
