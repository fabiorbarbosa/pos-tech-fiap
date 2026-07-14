import csv
import json
from pathlib import Path


def convert_uhhc_instance(path: str | Path) -> dict[str, list[dict[str, str]]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    terminal = data["terminal_points"][0]

    stops = [
        {
            "stop_id": terminal["id"],
            "name": "Terminal de Saida",
            "x": str(terminal["location"][0]),
            "y": str(terminal["location"][1]),
            "demand": "0",
            "priority": "0",
            "is_depot": "true",
        }
    ]

    for patient in data["patients"]:
        duration = sum(service.get("duration", 0) for service in patient["required_services"])
        priority = _priority_from_time_window(patient["time_windows"])
        stops.append(
            {
                "stop_id": patient["id"],
                "name": patient["id"],
                "x": str(patient["location"][0]),
                "y": str(patient["location"][1]),
                "demand": str(max(1, round(duration / 15))),
                "priority": str(priority),
                "is_depot": "false",
            }
        )

    vehicles = []
    for caregiver in data["caregivers"]:
        shift = caregiver["working_shift"]
        capacity = sum(1 for _ in caregiver.get("abilities", [])) * 4 or 4
        max_distance = max(20, shift["end"] - shift["start"])
        vehicles.append(
            {
                "vehicle_id": caregiver["id"],
                "capacity": str(capacity),
                "max_distance": str(max_distance),
            }
        )

    return {"stops": stops, "vehicles": vehicles}


def write_converted_csvs(instance_path: str | Path, output_dir: str | Path) -> tuple[Path, Path]:
    converted = convert_uhhc_instance(instance_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stops_path = output_dir / "stops_from_uhhc.csv"
    vehicles_path = output_dir / "vehicles_from_uhhc.csv"

    _write_csv(stops_path, converted["stops"])
    _write_csv(vehicles_path, converted["vehicles"])
    return stops_path, vehicles_path


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _priority_from_time_window(time_windows: list[dict[str, float]]) -> int:
    earliest_start = min(window["start"] for window in time_windows)
    if earliest_start <= 60:
        return 5
    if earliest_start <= 180:
        return 4
    if earliest_start <= 300:
        return 3
    if earliest_start <= 420:
        return 2
    return 1
