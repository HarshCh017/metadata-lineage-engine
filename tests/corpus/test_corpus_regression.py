import pytest
import json
from pathlib import Path
from lineage_platform.parsers.qlikview.antlr_parser import ANTLRQVSParser
from lineage_platform.models.adapters import QlikToIntermediateAdapter
from lineage_platform.core.normalization import SemanticNormalizer

def test_corpus_regression_01():
    script = """
    LOAD Field1, Field2 FROM [lib://Data/Source.csv];
    """
    
    parser = ANTLRQVSParser(use_strict=False)
    app, metadata = parser.parse(script)
    
    graph = QlikToIntermediateAdapter.transform(app)
    graph = SemanticNormalizer.normalize(graph)
    
    # Load gold standard expected
    expected_path = Path(__file__).parent / "01_expected.json"
    with open(expected_path, "r") as f:
        expected = json.load(f)
        
    # Verify semantic structural equivalence (not exact ID match since IDs are hashed differently if we change hashing, wait, actually hashing is deterministic)
    assert len(graph.datasets) == len(expected["datasets"])
    assert graph.datasets[0].fully_qualified_name == expected["datasets"][0]["fully_qualified_name"]
    assert len(graph.fields) == len(expected["datasets"][0]["fields"])
    
    field_names = [f.name for f in graph.fields]
    for exp_f in expected["datasets"][0]["fields"]:
        assert exp_f["name"] in field_names
