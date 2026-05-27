import re
from typing import List

from lineage_platform.models.qlik_models import (
    QVSConnection
)


class ConnectionParser:

    """
    Extracts QlikView connection metadata.
    """

    CONNECTION_PATTERN = re.compile(
        r"LIB CONNECT TO\s+'([^']+)'",
        re.IGNORECASE
    )

    @classmethod
    def extract_connections(
        cls,
        content: str
    ) -> List[QVSConnection]:

        connections = []

        matches = cls.CONNECTION_PATTERN.findall(
            content
        )

        for match in matches:

            connection_name = match.strip()

            connections.append(

                QVSConnection(

                    connection_name=connection_name,

                    connection_string=connection_name,

                    database_type="UNKNOWN"

                )
            )

        return connections