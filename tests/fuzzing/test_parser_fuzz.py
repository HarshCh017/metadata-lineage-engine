import pytest
import random
import string
from lineage_platform.parsers.qlikview.antlr_parser import ANTLRQVSParser

def generate_malformed_script(base_script: str, mutation_rate: float = 0.1) -> str:
    """
    Intentionally corrupt a script to test parser resilience.
    """
    chars = list(base_script)
    for i in range(len(chars)):
        if random.random() < mutation_rate:
            mutation_type = random.choice(["delete", "insert", "swap", "unclose_quote", "unclose_bracket"])
            if mutation_type == "delete":
                chars[i] = ""
            elif mutation_type == "insert":
                chars[i] = chars[i] + random.choice(string.printable)
            elif mutation_type == "swap" and i < len(chars) - 1:
                chars[i], chars[i+1] = chars[i+1], chars[i]
            elif mutation_type == "unclose_quote":
                chars[i] = "'"
            elif mutation_type == "unclose_bracket":
                chars[i] = "["
    return "".join(chars)

@pytest.mark.parametrize("iteration", range(10)) # Limited to 10 for standard tests, 1000 in CI config
def test_parser_fuzz_resilience(iteration):
    base_script = """
    SET vVar = 1;
    LOAD Field1, Field2 FROM [lib://Data/Source.csv];
    SQL SELECT * FROM physical_table;
    """
    
    # Generate fuzzed script
    fuzzed_script = generate_malformed_script(base_script, mutation_rate=0.05)
    
    parser = ANTLRQVSParser(use_strict=False)
    
    try:
        # The parser must NOT crash with ValueError, IndexError, etc.
        # It must safely return the app, even if fallback was triggered and the app is empty.
        app, metadata = parser.parse(fuzzed_script)
        
        # Verify it handled it (either parsed it or fell back)
        assert metadata.parser_engine in ["ANTLR", "REGEX_FALLBACK"]
    except Exception as e:
        pytest.fail(f"Fuzzer crashed the parser with an unhandled exception: {str(e)}")
