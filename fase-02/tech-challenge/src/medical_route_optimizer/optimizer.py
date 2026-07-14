import math
import random

from .models import OptimizationResult, Stop, Vehicle, VehicleRoute


def optimize_routes(
    stops: list[Stop],
    vehicles: list[Vehicle],
    population_size: int = 80,
    generations: int = 120,
    mutation_rate: float = 0.15,
    elite_size: int = 2,
    random_seed: int | None = None,
) -> OptimizationResult:
    if random_seed is not None:
        random.seed(random_seed)

    depot = _get_depot(stops)
    deliveries = [stop for stop in stops if not stop.is_depot]
    stop_ids = [stop.stop_id for stop in deliveries]
    stop_lookup = {stop.stop_id: stop for stop in deliveries}

    population = [random.sample(stop_ids, len(stop_ids)) for _ in range(population_size)]
    history: list[float] = []
    best_sequence: list[str] = []
    best_routes: list[VehicleRoute] = []
    best_fitness = float("inf")
    best_total_distance = float("inf")

    for _ in range(generations):
        scored_population = []
        for sequence in population:
            routes, total_distance, fitness = _evaluate_sequence(sequence, depot, stop_lookup, vehicles)
            scored_population.append((fitness, total_distance, sequence, routes))

        scored_population.sort(key=lambda item: item[0])
        best_generation = scored_population[0]
        history.append(best_generation[0])

        if best_generation[0] < best_fitness:
            best_fitness = best_generation[0]
            best_total_distance = best_generation[1]
            best_sequence = list(best_generation[2])
            best_routes = best_generation[3]

        new_population = [list(item[2]) for item in scored_population[:elite_size]]
        while len(new_population) < population_size:
            parent_a = _tournament_selection(scored_population)
            parent_b = _tournament_selection(scored_population)
            child = _order_crossover(parent_a, parent_b)
            child = _mutate(child, mutation_rate)
            new_population.append(child)
        population = new_population

    return OptimizationResult(
        routes=best_routes,
        best_sequence=best_sequence,
        best_fitness=best_fitness,
        total_distance=best_total_distance,
        history=history,
    )


def _get_depot(stops: list[Stop]) -> Stop:
    for stop in stops:
        if stop.is_depot:
            return stop
    raise ValueError("At least one depot is required.")


def _evaluate_sequence(
    sequence: list[str],
    depot: Stop,
    stop_lookup: dict[str, Stop],
    vehicles: list[Vehicle],
) -> tuple[list[VehicleRoute], float, float]:
    routes: list[VehicleRoute] = []
    total_distance = 0.0
    fitness = 0.0
    remaining = list(sequence)

    for vehicle in vehicles:
        assigned_ids: list[str] = []
        while remaining:
            candidate = stop_lookup[remaining[0]]
            trial_ids = assigned_ids + [candidate.stop_id]
            trial_distance = _route_distance(trial_ids, depot, stop_lookup)
            trial_load = _route_load(trial_ids, stop_lookup)

            if trial_load <= vehicle.capacity and trial_distance <= vehicle.max_distance:
                assigned_ids.append(remaining.pop(0))
                continue

            if assigned_ids:
                break

            assigned_ids.append(remaining.pop(0))
            break

        route = _build_vehicle_route(vehicle, assigned_ids, depot, stop_lookup)
        routes.append(route)
        total_distance += route.distance
        fitness += route.distance
        fitness += route.capacity_overflow * 100.0
        fitness += route.distance_overflow * 10.0
        fitness += _priority_penalty(route.stop_ids, stop_lookup)

    if remaining:
        for index, stop_id in enumerate(remaining):
            vehicle = vehicles[index % len(vehicles)]
            route = routes[index % len(routes)]
            appended_ids = route.stop_ids + [stop_id]
            replacement = _build_vehicle_route(vehicle, appended_ids, depot, stop_lookup)
            total_distance += replacement.distance - route.distance
            fitness += replacement.distance - route.distance
            fitness += (replacement.capacity_overflow - route.capacity_overflow) * 100.0
            fitness += (replacement.distance_overflow - route.distance_overflow) * 10.0
            fitness += _priority_penalty([stop_id], stop_lookup) + len(route.stop_ids) * stop_lookup[stop_id].priority * 5.0
            routes[index % len(routes)] = replacement

    return routes, round(total_distance, 2), round(fitness, 2)


def _build_vehicle_route(
    vehicle: Vehicle,
    stop_ids: list[str],
    depot: Stop,
    stop_lookup: dict[str, Stop],
) -> VehicleRoute:
    distance = _route_distance(stop_ids, depot, stop_lookup)
    load = _route_load(stop_ids, stop_lookup)
    capacity_overflow = max(0, load - vehicle.capacity)
    distance_overflow = max(0.0, distance - vehicle.max_distance)
    return VehicleRoute(
        vehicle_id=vehicle.vehicle_id,
        stop_ids=list(stop_ids),
        distance=round(distance, 2),
        load=load,
        capacity_overflow=capacity_overflow,
        distance_overflow=round(distance_overflow, 2),
    )


def _route_distance(stop_ids: list[str], depot: Stop, stop_lookup: dict[str, Stop]) -> float:
    if not stop_ids:
        return 0.0

    distance = _distance(depot, stop_lookup[stop_ids[0]])
    for current, nxt in zip(stop_ids, stop_ids[1:]):
        distance += _distance(stop_lookup[current], stop_lookup[nxt])
    distance += _distance(stop_lookup[stop_ids[-1]], depot)
    return distance


def _route_load(stop_ids: list[str], stop_lookup: dict[str, Stop]) -> int:
    return sum(stop_lookup[stop_id].demand for stop_id in stop_ids)


def _priority_penalty(stop_ids: list[str], stop_lookup: dict[str, Stop]) -> float:
    return sum((index + 1) * stop_lookup[stop_id].priority * 5.0 for index, stop_id in enumerate(stop_ids))


def _distance(point_a: Stop, point_b: Stop) -> float:
    return math.dist((point_a.x, point_a.y), (point_b.x, point_b.y))


def _tournament_selection(scored_population: list[tuple[float, float, list[str], list[VehicleRoute]]]) -> list[str]:
    contenders = random.sample(scored_population, k=min(3, len(scored_population)))
    contenders.sort(key=lambda item: item[0])
    return list(contenders[0][2])


def _order_crossover(parent_a: list[str], parent_b: list[str]) -> list[str]:
    if len(parent_a) < 2:
        return list(parent_a)

    start, end = sorted(random.sample(range(len(parent_a)), 2))
    child = [None] * len(parent_a)
    child[start : end + 1] = parent_a[start : end + 1]

    insert_positions = [index for index, value in enumerate(child) if value is None]
    remaining_genes = [gene for gene in parent_b if gene not in child]

    for index, gene in zip(insert_positions, remaining_genes):
        child[index] = gene

    return [gene for gene in child if gene is not None]


def _mutate(sequence: list[str], mutation_rate: float) -> list[str]:
    mutated = list(sequence)
    if len(mutated) < 2 or random.random() >= mutation_rate:
        return mutated

    first, second = random.sample(range(len(mutated)), 2)
    mutated[first], mutated[second] = mutated[second], mutated[first]
    return mutated
