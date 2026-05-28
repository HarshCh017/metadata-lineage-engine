import re
from typing import Dict
from prometheus_client import Counter

MACRO_EXPANSIONS = Counter("qlikview_macro_expansions_total", "Total $(var) macro expansions performed")


class VariableParser:
    """
    Extracts QlikView variables (SET and LET) and expands macros.
    """

    SET_PATTERN = re.compile(r"^\s*(?:SET|LET)\s+([A-Za-z0-9_]+)\s*=\s*(.*?);", re.IGNORECASE | re.MULTILINE)

    @staticmethod
    def extract_variables(content: str) -> Dict[str, str]:
        variables = {}
        matches = VariableParser.SET_PATTERN.findall(content)
        for name, value in matches:
            variables[name.strip()] = value.strip()
        return variables

    @staticmethod
    def expand_macros(content: str, variables: Dict[str, str]) -> str:
        """
        Expands $(varName) macros in the script using the extracted variables.
        Resolves nested variables up to 3 levels deep.
        """
        def replace_macro(match):
            var_name = match.group(1).strip()
            # We must handle case-insensitive lookup since dictionary keys might not exactly match
            for k, v in variables.items():
                if k.lower() == var_name.lower():
                    MACRO_EXPANSIONS.inc()
                    return v
            return match.group(0)

        for _ in range(3):
            original = content
            content = re.sub(r"\$\(\s*([A-Za-z0-9_]+)\s*\)", replace_macro, content)
            if content == original:
                break
        return content
