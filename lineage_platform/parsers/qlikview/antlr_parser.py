import time
import structlog
from dataclasses import dataclass
from typing import Tuple, Any

from lineage_platform.parsers.qlikview.qvs_parser import QVSParser
from lineage_platform.models.qlik_models import QlikViewApp

logger = structlog.get_logger()

@dataclass
class ParseResultMetadata:
    parser_engine: str
    fallback_triggered: bool
    parse_duration_ms: float
    errors: list[str]

class ParserFailure(Exception):
    pass

class ANTLRQVSParser:
    """
    Enterprise entrypoint for Qlik parsing.
    Attempts strict AST parsing via ANTLR4. Falls back to Regex parsing on failure
    (e.g., timeout, syntax explosion, missing generated classes).
    """

    def __init__(self, use_strict: bool = True):
        self.use_strict = use_strict
        self.regex_parser = QVSParser()

    def parse(self, content: str) -> Tuple[QlikViewApp, ParseResultMetadata]:
        start_time = time.time()
        metadata = ParseResultMetadata(
            parser_engine="ANTLR",
            fallback_triggered=False,
            parse_duration_ms=0.0,
            errors=[]
        )

        try:
            # If not in strict mode, immediately fallback to Regex
            if not self.use_strict:
                raise ParserFailure("Strict parsing disabled by configuration.")

            # Attempt to import generated ANTLR components
            try:
                from .generated.QlikViewLexer import QlikViewLexer
                from .generated.QlikViewParser import QlikViewParser
                from antlr4 import InputStream, CommonTokenStream
                from .antlr_visitor import QlikViewASTVisitor
            except ImportError:
                raise ParserFailure("ANTLR generated classes missing. Run grammar compilation step.")

            # Initialize ANTLR Lexer/Parser and Visitor
            input_stream = InputStream(content)
            lexer = QlikViewLexer(input_stream)
            stream = CommonTokenStream(lexer)
            parser = QlikViewParser(stream)
            tree = parser.script()
            
            visitor = QlikViewASTVisitor()
            app = visitor.visit(tree)
            
            # If the tree visit yielded no loads and no variables but we had script content, fallback
            if len(app.loads) == 0 and len(app.variables) == 0 and len(content.strip()) > 50:
                raise ParserFailure("ANTLR traversal yielded empty results. Falling back to Regex.")

            # Success
            return app, metadata

        except ParserFailure as e:
            logger.warning("antlr_parsing_failed", reason=str(e), action="falling_back_to_regex")
            metadata.fallback_triggered = True
            metadata.parser_engine = "REGEX_FALLBACK"
            metadata.errors.append(str(e))
            
            # Execute emergency regex parser
            script_node = self.regex_parser.parse(content)

        except Exception as e:
            # Catch memory overflows or deep recursion limits
            logger.error("critical_parser_failure", error=str(e))
            metadata.fallback_triggered = True
            metadata.parser_engine = "REGEX_FALLBACK"
            metadata.errors.append(f"Critical overflow: {str(e)}")
            
            script_node = self.regex_parser.parse(content)

        metadata.parse_duration_ms = (time.time() - start_time) * 1000
        
        return script_node, metadata
