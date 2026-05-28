from lineage_platform.parsers.qlikview.variable_parser import VariableParser


def test_set_variable():
    script = "SET vTable = 'Users';"
    vars = VariableParser.extract_variables(script)
    assert vars["vTable"] == "'Users'"


def test_let_variable():
    script = "LET vDate = Today();"
    vars = VariableParser.extract_variables(script)
    assert vars["vDate"] == "Today()"


def test_macro_expansion():
    script = """
    SET vTable = Users;
    LOAD * FROM $(vTable);
    """
    vars = VariableParser.extract_variables(script)
    expanded = VariableParser.expand_macros(script, vars)
    assert "LOAD * FROM Users;" in expanded
    assert "$(vTable)" not in expanded


def test_missing_macro():
    script = "LOAD * FROM $(vUnknown);"
    expanded = VariableParser.expand_macros(script, {})
    assert "$(vUnknown)" in expanded
