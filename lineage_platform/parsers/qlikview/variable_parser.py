import re
from typing import Dict

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
        for _ in range(3):
            original = content
            for name, value in variables.items():
                content = re.sub(r"\$\(\s*" + re.escape(name) + r"\s*\)", value, content, flags=re.IGNORECASE)
            if content == original:
                break
        return content
