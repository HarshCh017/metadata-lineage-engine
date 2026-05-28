import re
from typing import List, Optional

from lineage_platform.models.qlik_models import QVSJoin


class JoinParser:
    """
    Parse QlikView JOIN statements.

    Supports:
    - LEFT JOIN LOAD ...
    - INNER JOIN (Orders) LOAD ...
    """

    EXPLICIT_JOIN_PATTERN = re.compile(r"(LEFT|INNER|RIGHT|FULL)?\s+(JOIN|KEEP)\s*\((.*?)\)", re.IGNORECASE | re.DOTALL)

    IMPLICIT_JOIN_PATTERN = re.compile(r"(LEFT|INNER|RIGHT|FULL)?\s+(JOIN|KEEP)\s+LOAD", re.IGNORECASE | re.DOTALL)

    RESIDENT_PATTERN = re.compile(r"RESIDENT\s+([a-zA-Z_]\w*)", re.IGNORECASE)

    @staticmethod
    def extract_joins(load_block: str, previous_table: Optional[str] = None) -> List[QVSJoin]:

        joins: List[QVSJoin] = []

        # ==================================================
        # EXPLICIT TARGET JOIN
        #
        # INNER JOIN (Orders)
        # ==================================================

        explicit_match = JoinParser.EXPLICIT_JOIN_PATTERN.search(load_block)

        if explicit_match:

            join_mod = (explicit_match.group(1) or "INNER").upper()
            join_action = explicit_match.group(2).upper()
            join_type = f"{join_mod} {join_action}"

            target_table = explicit_match.group(3).strip()

            resident_match = JoinParser.RESIDENT_PATTERN.search(load_block)

            if resident_match:

                source_table = resident_match.group(1).strip()

                joins.append(QVSJoin(join_type=join_type, source_table=source_table, target_table=target_table))

        # ==================================================
        # IMPLICIT TARGET JOIN
        #
        # LEFT JOIN LOAD ...
        # RESIDENT Customer;
        #
        # joins INTO previous table
        # ==================================================

        implicit_match = JoinParser.IMPLICIT_JOIN_PATTERN.search(load_block)

        if implicit_match and previous_table:

            join_mod = (implicit_match.group(1) or "INNER").upper()
            join_action = implicit_match.group(2).upper()
            join_type = f"{join_mod} {join_action}"

            resident_match = JoinParser.RESIDENT_PATTERN.search(load_block)

            if resident_match:

                source_table = resident_match.group(1).strip()

                joins.append(QVSJoin(join_type=join_type, source_table=source_table, target_table=previous_table))

        return joins
