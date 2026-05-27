import re
from typing import List

from lineage_platform.models.qlik_models import (
    QVSJoin
)


class JoinParser:

    """
    Parse QlikView JOIN statements.

    Supports:
    - LEFT JOIN LOAD ...
    - INNER JOIN (Orders) LOAD ...
    """

    EXPLICIT_JOIN_PATTERN = re.compile(
        r'(LEFT|INNER|RIGHT|FULL)?\s+JOIN\s*\((.*?)\)',
        re.IGNORECASE | re.DOTALL
    )

    IMPLICIT_JOIN_PATTERN = re.compile(
        r'(LEFT|INNER|RIGHT|FULL)?\s+JOIN\s+LOAD',
        re.IGNORECASE | re.DOTALL
    )

    RESIDENT_PATTERN = re.compile(
        r'RESIDENT\s+([a-zA-Z_]\w*)',
        re.IGNORECASE
    )

    @staticmethod
    def extract_joins(
        load_block: str,
        previous_table: str = None
    ) -> List[QVSJoin]:

        joins = []

        # ==================================================
        # EXPLICIT TARGET JOIN
        #
        # INNER JOIN (Orders)
        # ==================================================

        explicit_match = (
            JoinParser.EXPLICIT_JOIN_PATTERN.search(
                load_block
            )
        )

        if explicit_match:

            join_type = (
                explicit_match.group(1)
                or 'INNER'
            ).upper()

            target_table = (
                explicit_match.group(2).strip()
            )

            resident_match = (
                JoinParser.RESIDENT_PATTERN.search(
                    load_block
                )
            )

            if resident_match:

                source_table = (
                    resident_match.group(1).strip()
                )

                joins.append(
                    QVSJoin(
                        join_type=join_type,
                        source_table=source_table,
                        target_table=target_table
                    )
                )

        # ==================================================
        # IMPLICIT TARGET JOIN
        #
        # LEFT JOIN LOAD ...
        # RESIDENT Customer;
        #
        # joins INTO previous table
        # ==================================================

        implicit_match = (
            JoinParser.IMPLICIT_JOIN_PATTERN.search(
                load_block
            )
        )

        if implicit_match and previous_table:

            join_type = (
                implicit_match.group(1)
                or 'INNER'
            ).upper()

            resident_match = (
                JoinParser.RESIDENT_PATTERN.search(
                    load_block
                )
            )

            if resident_match:

                source_table = (
                    resident_match.group(1).strip()
                )

                joins.append(
                    QVSJoin(
                        join_type=join_type,
                        source_table=source_table,
                        target_table=previous_table
                    )
                )

        return joins