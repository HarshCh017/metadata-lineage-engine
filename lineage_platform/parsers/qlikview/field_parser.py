import re
from typing import List


class FieldParser:

    @staticmethod
    def find_load_terminator(text: str) -> int:
        """
        Find the real terminating semicolon
        while ignoring semicolons inside:
        - strings
        - parentheses
        """

        in_single_quote = False
        in_double_quote = False
        paren_depth = 0

        for idx, char in enumerate(text):

            # ------------------------------------------
            # Track quoted strings
            # ------------------------------------------

            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote

            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote

            # ------------------------------------------
            # Track parentheses depth
            # ------------------------------------------

            elif char == "(":
                paren_depth += 1

            elif char == ")":

                if paren_depth > 0:
                    paren_depth -= 1

            # ------------------------------------------
            # Detect actual LOAD terminator
            # ------------------------------------------

            elif char == ";" and not in_single_quote and not in_double_quote and paren_depth == 0:
                return idx

        return -1

    # ======================================================
    # FIELD EXTRACTION
    # ======================================================

    @staticmethod
    def extract_fields(load_block: str) -> List[str]:
        """
        Extract fields from a LOAD block.

        Handles:
        - simple fields
        - aliased fields
        - function expressions
        - nested functions
        - multiline LOAD statements
        """

        # --------------------------------------------------
        # Locate LOAD keyword
        # --------------------------------------------------

        load_match = re.search(r"LOAD\s+(.*)", load_block, re.IGNORECASE | re.DOTALL)

        if not load_match:
            return []

        text_from_load = load_match.group(1)

        # --------------------------------------------------
        # Stop at actual LOAD terminator
        # --------------------------------------------------

        semi_idx = FieldParser.find_load_terminator(text_from_load)

        if semi_idx != -1:
            field_section = text_from_load[:semi_idx]
        else:
            field_section = text_from_load

        # --------------------------------------------------
        # Split fields safely
        # Ignore commas inside functions
        # --------------------------------------------------

        fields = []

        current: List[str] = []

        paren_depth = 0

        in_single_quote = False
        in_double_quote = False

        for char in field_section:

            # ----------------------------------------------
            # Quotes
            # ----------------------------------------------

            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote

            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote

            # ----------------------------------------------
            # Parentheses
            # ----------------------------------------------

            elif char == "(":
                paren_depth += 1

            elif char == ")":

                if paren_depth > 0:
                    paren_depth -= 1

            # ----------------------------------------------
            # Split only at top-level commas
            # ----------------------------------------------

            if char == "," and paren_depth == 0 and not in_single_quote and not in_double_quote:

                field = "".join(current).strip()

                if field:
                    fields.append(field)

                current = []

            else:
                current.append(char)

        # --------------------------------------------------
        # Final field
        # --------------------------------------------------

        final_field = "".join(current).strip()

        if final_field:
            fields.append(final_field)

        # --------------------------------------------------
        # Cleanup fields
        # --------------------------------------------------

        cleaned_fields = []

        invalid_fields = {"sql select", "from", "where", "group by", "resident", "load", "select"}

        for field in fields:

            field = field.strip()

            # Remove trailing semicolon
            field = field.rstrip(";")

            # Skip empty
            if not field:
                continue

            lower_field = field.lower()

            # Skip invalid parser artifacts
            if lower_field in invalid_fields:
                continue

            # Skip SQL FROM clauses accidentally captured
            if lower_field.startswith("from "):
                continue

            # --------------------------------------------------
            # Extract aliases
            # Example:
            # UPPER(Name) AS Name_Upper
            # -> Name_Upper
            # --------------------------------------------------

            alias_match = re.search(r"\s+AS\s+([A-Za-z0-9_]+)", field, flags=re.IGNORECASE)

            if alias_match:

                cleaned_fields.append(alias_match.group(1))

            else:

                # --------------------------------------------------
                # ApplyMap extraction
                # --------------------------------------------------
                apply_map_match = re.search(r"ApplyMap\s*\(\s*['\"][^'\"]+['\"]\s*,\s*([A-Za-z0-9_]+)", field, flags=re.IGNORECASE)
                if apply_map_match:
                    cleaned_fields.append(apply_map_match.group(1))
                else:
                    cleaned_fields.append(field.strip())

        return cleaned_fields
