import structlog
from prometheus_client import Counter, Histogram, REGISTRY

logger = structlog.get_logger()

class TelemetryManager:
    """
    Centralized Observability Layer.
    Consolidates parser metrics, Neo4j latency, and error rates.
    """
    _initialized = False

    @classmethod
    def init_metrics(cls):
        if cls._initialized:
            return
            
        try:
            cls.FILES_PARSED = Counter("qlikview_files_parsed_total", "Total QlikView files parsed")
            cls.PARSE_FAILURES = Counter("qlikview_parse_failures_total", "Total parse failures")
            cls.FALLBACK_RATES = Counter("qlikview_fallback_parse_total", "Total regex fallbacks triggered")
            cls.INCLUDES_RESOLVED = Counter("qlikview_includes_resolved_total", "Total $(Include=...) directives resolved")
            cls.MACRO_EXPANSIONS = Counter("qlikview_macro_expansions_total", "Total $(var) macro expansions performed")
            
            cls.GRAPH_INSERT_LATENCY = Histogram("neo4j_batch_insert_seconds", "Latency of Neo4j graph batch writes")
            cls.PARSE_LATENCY = Histogram("qlikview_parse_latency_seconds", "Latency of QlikView parsing phase")
        except ValueError:
            # Handle duplicate registration during pytest re-imports
            cls.FILES_PARSED = REGISTRY._names_to_collectors["qlikview_files_parsed_total"]
            cls.PARSE_FAILURES = REGISTRY._names_to_collectors["qlikview_parse_failures_total"]
            cls.FALLBACK_RATES = REGISTRY._names_to_collectors["qlikview_fallback_parse_total"]
            cls.INCLUDES_RESOLVED = REGISTRY._names_to_collectors["qlikview_includes_resolved_total"]
            cls.MACRO_EXPANSIONS = REGISTRY._names_to_collectors["qlikview_macro_expansions_total"]
            
            cls.GRAPH_INSERT_LATENCY = REGISTRY._names_to_collectors["neo4j_batch_insert_seconds"]
            cls.PARSE_LATENCY = REGISTRY._names_to_collectors["qlikview_parse_latency_seconds"]
            
        cls._initialized = True

# Initialize metrics on import
TelemetryManager.init_metrics()
