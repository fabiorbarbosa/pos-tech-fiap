from pathlib import Path

from medical_route_optimizer.io_utils import load_stops, load_vehicles
from medical_route_optimizer.optimizer import optimize_routes
from medical_route_optimizer.reporting import build_driver_instructions, build_operations_report


FIXTURES = Path(__file__).resolve().parents[1] / "dataset"
SAMPLES = FIXTURES / "samples"


def test_optimizer_covers_all_non_depot_stops_once():
    stops = load_stops(SAMPLES / "stops_sample_100.csv")
    vehicles = load_vehicles(SAMPLES / "vehicles_sample_100_experiment.csv")

    result = optimize_routes(
        stops=stops,
        vehicles=vehicles,
        population_size=30,
        generations=20,
        mutation_rate=0.2,
        random_seed=7,
    )

    delivered_stop_ids = [stop_id for route in result.routes for stop_id in route.stop_ids]
    expected_stop_ids = sorted(stop.stop_id for stop in stops if not stop.is_depot)

    assert sorted(delivered_stop_ids) == expected_stop_ids
    assert result.best_fitness > 0
    assert len(result.history) == 20


def test_driver_instructions_include_vehicle_and_stops():
    stops = load_stops(SAMPLES / "stops_sample_100.csv")
    vehicles = load_vehicles(SAMPLES / "vehicles_sample_100_experiment.csv")
    result = optimize_routes(
        stops=stops,
        vehicles=vehicles,
        population_size=20,
        generations=10,
        mutation_rate=0.1,
        random_seed=3,
    )

    instructions = build_driver_instructions(result, stops)

    assert "Veiculo motorcycle" in instructions
    assert "Store Depot" in instructions
    assert "medicamentos_criticos" in instructions or "insumos_medicos" in instructions


def test_operations_report_mentions_priority_and_distance():
    stops = load_stops(SAMPLES / "stops_sample_100.csv")
    vehicles = load_vehicles(SAMPLES / "vehicles_sample_100_experiment.csv")
    result = optimize_routes(
        stops=stops,
        vehicles=vehicles,
        population_size=20,
        generations=10,
        mutation_rate=0.1,
        random_seed=11,
    )

    report = build_operations_report(result, stops, vehicles)

    assert "distancia total" in report.lower()
    assert "prioridade" in report.lower()
    assert "algoritmo genetico" in report.lower()
