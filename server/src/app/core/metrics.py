from prometheus_client import Counter, Histogram


symbolic_evaluations_total = Counter(
    "symbolic_evaluations_total",
    "Número total de execuções simbólicas realizadas",
    ['flow_id']
)

symbolic_inconsistencies_ratio = Histogram(
    "symbolic_inconsistencies_ratio",
    "Distribuição temporal do ratio de inconsistências",
    ["flow_id"],
    buckets=[0, 0.1, 0.3, 0.6, 1.0, 2.0, 5.0]
)

symbolic_evolution_index_events = Histogram(
    'symbolic_evolution_index_events',
    'Índice de evolução simbólica entre execuções consecutivas ao longo do tempo (-1 a +1)',
    ['flow_id'],
    buckets=[0, 0.5, 1.0, 1.5, 2.0]
)

symbolic_time_to_modification_seconds = Histogram(
    "symbolic_time_to_modification_seconds",
    "Tempo entre última execução simbólica e modificação do fluxo (segundos)",
    ['flow_id']
)

symbolic_evaluation_duration_seconds = Histogram(
    "symbolic_evaluation_duration_seconds",
    "Tempo de execução simbólica (segundos)",
    buckets=[0.01, 0.05, 0.1, 0.3, 0.6, 1, 2, 5]
)

symbolic_solver_timeout_total = Counter(
    "symbolic_solver_timeout_total",
    "Quantidade de execuções simbólicas que atingiram o timeout"
)

symbolic_solver_errors_total = Counter(
    "symbolic_solver_errors_total",
    "Quantidade de erros internos do executor simbólico"
)
