from prometheus_client import Counter, Histogram, Gauge


# Prometheus Metrics Definitions
# Per Flow Metrics
inconsistencies_ratio = Gauge(
    "inconsistencies_ratio",
    "Razão de inconsistências sobre o total de condições para um fluxo específico",
    ["flow_id"]
)

evolution_index = Gauge(
    "evolution_index",
    "Índice de evolução (-1 a 1) para um fluxo específico",
    ["flow_id"]
)

time_to_modification_seconds = Gauge(
    "time_to_modification_seconds",
    "Tempo em segundos entre a última execução simbólica e a modificação do fluxo",
    ["flow_id"]
)

tests_total = Counter(
    "tests_total",
    "Total de execuções simbólicas do fluxo",
    ["flow_id"]
)

# Global Metrics
execution_errors_total = Counter(
    "execution_errors_total",
    "Número total de erros na execução simbólica",
)
execution_timeouts_total = Counter(
    "execution_timeouts_total",
    "Número total de timeouts durante a execução simbólica"
)
execution_duration_seconds = Histogram(
    "execution_duration_seconds",
    "Duração da execução simbólica em segundos",
    buckets=[0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 30, 60]
)
