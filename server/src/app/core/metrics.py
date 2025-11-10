from prometheus_client import Counter, Gauge, Histogram


symbolic_evaluations_total = Counter(
    "symbolic_evaluations_total",
    "Número total de execuções simbólicas realizadas"
)

symbolic_evaluation_duration_seconds = Histogram(
    "symbolic_evaluation_duration_seconds",
    "Tempo de execução simbólica (segundos)"
)

symbolic_inconsistencies_ratio = Gauge(
    "symbolic_inconsistencies_ratio",
    "Proporção de inconsistências (reductions + pruned) em relação ao total de condições",
    ["flow_id"]
)

symbolic_evolution_index_gauge = Gauge(
    'symbolic_evolution_index',
    'Índice de evolução simbólica entre execuções consecutivas (-1 a +1)',
    ['flow_id']
)

symbolic_time_to_modification_seconds = Histogram(
    "symbolic_time_to_modification_seconds",
    "Tempo entre última execução simbólica e modificação do fluxo (segundos)",
)
