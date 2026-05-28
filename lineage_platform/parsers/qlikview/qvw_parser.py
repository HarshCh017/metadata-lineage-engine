import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
import re
from lineage_platform.models.qlik_models import QVSSheet, QVSChart


class QVWParser:
    """
    Parses Qlik Document Analyzer XML metadata to extract Dashboard Lineage.
    """

    @staticmethod
    def parse_metadata(xml_path: str) -> List[QVSSheet]:
        path = Path(xml_path)
        if not path.exists():
            print(f"XML metadata not found at {xml_path}")
            return []

        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Failed to parse XML metadata: {e}")
            return []

        sheets = []

        # XML Schema per plan:
        # <Documents>/<Document>/<Sheets>/<Sheet>/<Objects>/<TextObject|ChartObject|TableObject>/<Dimensions|Expressions>

        sheet_nodes = root.findall("./Document/Sheets/Sheet")
        if not sheet_nodes:
            # Fallback for simpler XMLs if needed
            sheet_nodes = root.findall(".//Sheet")

        for sheet_node in sheet_nodes:
            sheet_id = sheet_node.get("Id", sheet_node.get("id", "UNKNOWN_SHEET"))

            title_node = sheet_node.find("Title")
            if title_node is None:
                title_node = sheet_node.find("title")
            sheet_title = title_node.text if title_node is not None and title_node.text else sheet_id

            sheet = QVSSheet(sheet_id=sheet_id, title=sheet_title, charts=[])

            # Find all objects within this sheet
            objects_node = sheet_node.find("Objects")
            if objects_node is not None:
                # Get all children of Objects (TextObject, ChartObject, TableObject, etc.)
                chart_nodes = list(objects_node)
            else:
                # Fallback
                chart_nodes = sheet_node.findall(".//SheetObject")

            for chart_node in chart_nodes:
                chart_id = chart_node.get("Id", chart_node.get("id", "UNKNOWN_CHART"))

                c_title_node = chart_node.find("Title")
                if c_title_node is None:
                    c_title_node = chart_node.find("title")
                chart_title = c_title_node.text if c_title_node is not None and c_title_node.text else chart_id

                chart = QVSChart(chart_id=chart_id, title=chart_title, fields=[])

                # Extract fields from <Dimensions> and <Expressions>
                fields_to_parse = []

                dimensions = chart_node.find("Dimensions")
                if dimensions is not None:
                    for dim in dimensions:
                        if dim.text:
                            fields_to_parse.append(dim.text)

                expressions = chart_node.find("Expressions")
                if expressions is not None:
                    for expr in expressions:
                        if expr.text:
                            fields_to_parse.append(expr.text)

                # Fallback if no Dimensions/Expressions found
                if not fields_to_parse:
                    def_nodes = chart_node.findall(".//Definition")
                    for def_node in def_nodes:
                        if def_node.text:
                            fields_to_parse.append(def_node.text)

                for field_text in fields_to_parse:
                    tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", field_text)
                    for t in tokens:
                        if t.upper() not in {"SUM", "AVG", "MIN", "MAX", "COUNT", "IF", "NULL", "AS", "AND", "OR"}:
                            if t not in chart.fields:
                                chart.fields.append(t)

                sheet.charts.append(chart)
            sheets.append(sheet)

        return sheets
