import re
from typing import List, Optional, Any

from lineage_platform.models.qlik_models import QVSField


class SyntheticFieldParser:
    """
    Enterprise-safe synthetic field parser.

    Extracts:
    - aliases
    - formulas
    - source fields
    - aggregations
    - IF statements
    - ApplyMap
    """

    FUNCTION_NAMES = {"SUM", "AVG", "COUNT", "MIN", "MAX", "IF", "UPPER", "LOWER", "APPLYMAP", "YEAR", "MONTH", "TODAY"}

    @classmethod
    def extract_synthetic_fields(cls, block: str, table_name: Optional[str] = None) -> List[QVSField]:

        synthetic_fields: List[Any] = []

        # -------------------------------------------------
        # Extract LOAD section only
        # -------------------------------------------------

        load_match = re.search(
            r"LOAD(.*?)" r"(RESIDENT|SQL SELECT|FROM|GROUP BY|;)", block, flags=(re.IGNORECASE | re.DOTALL)
        )

        if not load_match:

            return synthetic_fields

        load_content = load_match.group(1)

        # -------------------------------------------------
        # Split fields safely
        # -------------------------------------------------

        fields = re.split(r",\s*\n", load_content)

        for field in fields:

            field = field.strip()

            # ---------------------------------------------
            # Detect aliases
            # ---------------------------------------------

            alias_match = re.search(r"(.+?)\s+AS\s+([A-Za-z0-9_]+)", field, flags=re.IGNORECASE)

            if not alias_match:
                continue

            formula = alias_match.group(1).strip()

            alias = alias_match.group(2).strip()

            # ---------------------------------------------
            # Skip simple passthrough fields
            # Example:
            # CustomerID AS CustomerID
            # ---------------------------------------------

            if formula.upper() == alias.upper():
                continue

            # ---------------------------------------------
            # Extract source fields
            # ---------------------------------------------

            tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", formula)

            source_fields = []

            for token in tokens:

                upper = token.upper()

                # Skip functions

                if upper in cls.FUNCTION_NAMES:
                    continue

                # Skip numeric-like

                if token.isdigit():
                    continue

                # Skip common literals

                if upper in {"HIGH", "LOW", "ACTIVE", "INACTIVE", "UNKNOWN", "VIP", "STANDARD", "A"}:
                    continue

                # Avoid duplicates

                if token not in source_fields:

                    source_fields.append(token)

            # ---------------------------------------------
            # Create lineage field
            # ---------------------------------------------

            synthetic_fields.append(
                QVSField(
                    name=alias, table_name=table_name, formula=formula, is_synthetic=True, source_fields=source_fields
                )
            )

        return synthetic_fields
