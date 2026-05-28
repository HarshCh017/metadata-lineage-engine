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
        
        # Generic traversal assuming <Sheet> -> <SheetObject> -> <Definition>
        sheet_nodes = root.findall(".//Sheet")
        if not sheet_nodes:
            sheet_nodes = root.findall(".//sheet")
            
        for sheet_node in sheet_nodes:
            sheet_id = sheet_node.get("Id", sheet_node.get("id", "UNKNOWN_SHEET"))
            
            title_node = sheet_node.find("Title")
            if title_node is None:
                title_node = sheet_node.find("title")
            sheet_title = title_node.text if title_node is not None and title_node.text else sheet_id
            
            sheet = QVSSheet(sheet_id=sheet_id, title=sheet_title, charts=[])
            
            chart_nodes = sheet_node.findall(".//SheetObject")
            if not chart_nodes:
                chart_nodes = sheet_node.findall(".//sheetobject")
                
            for chart_node in chart_nodes:
                chart_id = chart_node.get("Id", chart_node.get("id", "UNKNOWN_CHART"))
                
                c_title_node = chart_node.find("Title")
                if c_title_node is None:
                    c_title_node = chart_node.find("title")
                chart_title = c_title_node.text if c_title_node is not None and c_title_node.text else chart_id
                
                chart = QVSChart(chart_id=chart_id, title=chart_title, fields=[])
                
                # Extract fields from definitions
                def_nodes = chart_node.findall(".//Definition")
                if not def_nodes:
                    def_nodes = chart_node.findall(".//definition")
                    
                for def_node in def_nodes:
                    if def_node.text:
                        # Extract basic field tokens from expressions (e.g. sum(Sales) -> Sales)
                        tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", def_node.text)
                        for t in tokens:
                            if t.upper() not in {"SUM", "AVG", "MIN", "MAX", "COUNT", "IF", "NULL", "AS", "AND", "OR"}:
                                if t not in chart.fields:
                                    chart.fields.append(t)
                                    
                sheet.charts.append(chart)
            sheets.append(sheet)
            
        return sheets
