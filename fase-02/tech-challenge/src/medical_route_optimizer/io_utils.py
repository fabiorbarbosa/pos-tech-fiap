import csv
from pathlib import Path

from .models import Stop, Vehicle


def load_stops(path: str | Path) -> list[Stop]:
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            Stop(
                stop_id=row["stop_id"],
                name=row["name"],
                x=float(row["x"]),
                y=float(row["y"]),
                demand=int(row["demand"]),
                priority=int(row["priority"]),
                is_depot=row["is_depot"].strip().lower() == "true",
            )
            for row in reader
        ]


def load_vehicles(path: str | Path) -> list[Vehicle]:
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            Vehicle(
                vehicle_id=row["vehicle_id"],
                capacity=int(row["capacity"]),
                max_distance=float(row["max_distance"]),
            )
            for row in reader
        ]
