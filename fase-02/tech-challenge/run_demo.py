from pathlib import Path

from medical_route_optimizer.io_utils import load_stops, load_vehicles
from medical_route_optimizer.optimizer import optimize_routes
from medical_route_optimizer.reporting import (
    build_driver_instructions,
    build_llm_prompt,
    build_operations_report,
)
from medical_route_optimizer.visualization import plot_history, plot_routes


def main() -> None:
    root = Path(__file__).resolve().parent
    dataset_dir = root / "dataset"
    results_dir = root / "results"
    figures_dir = root / "figures"
    samples_dir = dataset_dir / "samples"

    stops = load_stops(samples_dir / "stops_sample_100.csv")
    vehicles = load_vehicles(samples_dir / "vehicles_sample_100_experiment.csv")
    result = optimize_routes(
        stops=stops,
        vehicles=vehicles,
        population_size=120,
        generations=120,
        mutation_rate=0.10,
        elite_size=2,
        random_seed=42,
    )

    results_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    (results_dir / "driver_instructions_final.md").write_text(
        build_driver_instructions(result, stops),
        encoding="utf-8",
    )
    (results_dir / "operations_report_final.md").write_text(
        build_operations_report(result, stops, vehicles),
        encoding="utf-8",
    )
    (results_dir / "llm_prompt_final.txt").write_text(
        build_llm_prompt(result, stops, vehicles),
        encoding="utf-8",
    )

    plot_routes(result, stops, figures_dir / "rotas-otimizadas-final-clean.png")
    plot_history(result, figures_dir / "convergencia-ga-final.png")

    print(f"Fitness final: {result.best_fitness:.2f}")
    print(f"Distancia total: {result.total_distance:.2f}")
    for route in result.routes:
        print(
            f"{route.vehicle_id}: paradas={len(route.stop_ids)}, "
            f"distancia={route.distance:.2f}, carga={route.load}, "
            f"overflow_carga={route.capacity_overflow}, overflow_distancia={route.distance_overflow:.2f}"
        )
    print(f"Arquivos gerados em: {results_dir} e {figures_dir}")


if __name__ == "__main__":
    main()
