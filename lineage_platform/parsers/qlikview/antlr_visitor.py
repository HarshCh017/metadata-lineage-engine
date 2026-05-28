from typing import List, Dict, Any
# Note: The following imports will resolve after running ANTLR tool:
# `antlr4 -Dlanguage=Python3 QlikViewLexer.g4 QlikViewParser.g4`
try:
    from lineage_platform.grammar.qlikview.QlikViewParserVisitor import QlikViewParserVisitor
except ImportError:
    class QlikViewParserVisitor:
        pass # Mock until generated

class QlikViewASTVisitor(QlikViewParserVisitor):
    """
    Traverses the ANTLR AST to extract lineage metadata.
    Replaces the regex-based QVSParser.
    """

    def __init__(self):
        self.loads = []
        self.current_load = None

    def visitLoad_statement(self, ctx):
        """
        Visits a LOAD statement in the AST.
        """
        # Create a new load context
        self.current_load = {
            "type": "LOAD",
            "fields": [],
            "source": None
        }
        
        # Traverse children (field_list, source)
        self.visitChildren(ctx)
        
        # Save and reset
        if self.current_load:
            self.loads.append(self.current_load)
            self.current_load = None
            
        return None

    def visitField(self, ctx):
        if self.current_load:
            # Extract text from the identifier node
            field_name = ctx.identifier(0).getText()
            
            # Check for AS alias
            if len(ctx.identifier()) > 1:
                alias = ctx.identifier(1).getText()
                self.current_load["fields"].append({"name": field_name, "alias": alias})
            else:
                self.current_load["fields"].append({"name": field_name})
                
        return self.visitChildren(ctx)

    def visitSource(self, ctx):
        if self.current_load:
            self.current_load["source"] = ctx.getText()
        return self.visitChildren(ctx)
