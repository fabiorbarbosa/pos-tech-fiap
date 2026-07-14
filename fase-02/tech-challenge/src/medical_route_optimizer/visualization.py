from pathlib import Path

import matplotlib.pyplot as plt

from .models import OptimizationResult, Stop


def plot_routes(result: OptimizationResult, stops: list[Stop], output_path: str | Path) -> None:
    stop_lookup = {stop.stop_id: stop for stop in stops}
    depot = next(stop for stop in stops if stop.is_depot)
    plt.figure(figsize=(8, 6))

    for route in result.routes:
        x_points = [depot.x]
        y_points = [depot.y]
        labels = [depot.name]

        for stop_id in route.stop_ids:
            stop = stop_lookup[stop_id]
            x_points.append(stop.x)
            y_points.append(stop.y)
            labels.append(stop.name)

        x_points.append(depot.x)
        y_points.append(depot.y)
        labels.append(depot.name)

        plt.plot(x_points, y_points, marker="o", label=route.vehicle_id)
        for x_value, y_value, label in zip(x_points, y_points, labels):
            plt.text(x_value + 0.1, y_value + 0.1, label, fontsize=8)

    plt.title("Rotas otimizadas")
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_history(result: OptimizationResult, output_path: str | Path) -> None:
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(result.history) + 1), result.history)
    plt.title("Convergencia do algoritmo genetico")
    plt.xlabel("Geracao")
    plt.ylabel("Fitness")
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
