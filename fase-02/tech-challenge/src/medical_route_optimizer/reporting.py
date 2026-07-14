from .models import OptimizationResult, Stop, Vehicle


def build_driver_instructions(result: OptimizationResult, stops: list[Stop]) -> str:
    stop_lookup = {stop.stop_id: stop for stop in stops}
    depot_name = next(stop.name for stop in stops if stop.is_depot)
    sections = ["# Instrucoes de entrega", ""]

    for route in result.routes:
        sections.append(f"## Veiculo {route.vehicle_id}")
        sections.append(f"- Saida: {depot_name}")
        if not route.stop_ids:
            sections.append("- Nenhuma parada atribuida.")
            sections.append("")
            continue

        for index, stop_id in enumerate(route.stop_ids, start=1):
            stop = stop_lookup[stop_id]
            sections.append(
                f"- Parada {index}: {stop.stop_id} ({stop.name}) | demanda {stop.demand} | prioridade {stop.priority}"
            )
        sections.append(f"- Retorno: {depot_name}")
        sections.append(f"- Distancia estimada: {route.distance:.2f}")
        sections.append("")

    return "\n".join(sections).strip()


def build_operations_report(result: OptimizationResult, stops: list[Stop], vehicles: list[Vehicle]) -> str:
    high_priority = sorted((stop for stop in stops if not stop.is_depot), key=lambda stop: (-stop.priority, stop.name))
    route_lines = []
    for route in result.routes:
        route_lines.append(
            f"- {route.vehicle_id}: {len(route.stop_ids)} paradas, carga {route.load}, distancia {route.distance:.2f}"
        )

    return "\n".join(
        [
            "# Relatorio operacional",
            "",
            "## Resumo executivo",
            f"A solucao atual foi gerada com algoritmo genetico sobre {len(vehicles)} veiculos e {len(high_priority)} entregas.",
            f"A distancia total estimada e {result.total_distance:.2f}.",
            "",
            "## Rotas sugeridas",
            *route_lines,
            "",
            "## Prioridade",
            f"As entregas de maior prioridade sao: {', '.join(f'{stop.stop_id} ({stop.name})' for stop in high_priority[:3])}.",
            "",
            "## Proxima adaptacao",
            "Substituir a base sintetica pelos dados finais e recalibrar pesos de prioridade, capacidade e autonomia.",
        ]
    )


def build_llm_prompt(result: OptimizationResult, stops: list[Stop], vehicles: list[Vehicle]) -> str:
    stop_lookup = {stop.stop_id: stop for stop in stops}
    route_payload = []
    for route in result.routes:
        names = [f"{stop_id} ({stop_lookup[stop_id].name})" for stop_id in route.stop_ids]
        route_payload.append(
            f"{route.vehicle_id}: paradas={names}, carga={route.load}, distancia={route.distance:.2f}"
        )

    return "\n".join(
        [
            "Voce e um assistente logistico hospitalar.",
            "Gere instrucoes objetivas para motoristas e um resumo gerencial de eficiencia.",
            "Considere que prioridades mais altas devem aparecer primeiro na narrativa.",
            f"Veiculos disponiveis: {[vehicle.vehicle_id for vehicle in vehicles]}",
            f"Distancia total estimada: {result.total_distance:.2f}",
            "Rotas:",
            *route_payload,
        ]
    )
