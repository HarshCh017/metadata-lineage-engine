import pytest
from lineage_platform.parsers.qlikview.comment_cleaner import CommentCleaner

def test_single_line_comments():
    script = "LOAD A, B; // this is a comment\nLOAD C, D;"
    cleaned = CommentCleaner.clean_comments(script)
    assert "//" not in cleaned
    assert "LOAD A, B;" in cleaned
    assert "LOAD C, D;" in cleaned

def test_multi_line_comments():
    script = "LOAD A, B; /* this is a \n multiline \n comment */ LOAD C, D;"
    cleaned = CommentCleaner.clean_comments(script)
    assert "/*" not in cleaned
    assert "LOAD A, B;" in cleaned
    assert "LOAD C, D;" in cleaned

def test_rem_comments():
    script = "REM this is a weird legacy comment;\nLOAD A, B;"
    cleaned = CommentCleaner.clean_comments(script)
    assert "REM" not in cleaned
    assert "weird legacy comment" not in cleaned
    assert "LOAD A, B;" in cleaned

def test_combined_comments():
    script = """
    // header
    REM step 1;
    LOAD A, B /* inline */ ;
    """
    cleaned = CommentCleaner.clean_comments(script)
    assert "header" not in cleaned
    assert "step 1" not in cleaned
    assert "inline" not in cleaned
    assert "LOAD A, B  ;" in cleaned
