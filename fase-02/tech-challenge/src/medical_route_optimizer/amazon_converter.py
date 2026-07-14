import csv
from pathlib import Path


REQUIRED_COLUMNS = {
    "Order_ID",
    "Vehicle",
    "Store_Latitude",
    "Store_Longitude",
    "Drop_Latitude",
    "Drop_Longitude",
    "Traffic",
    "Weather",
    "Delivery_Time",
}

VEHICLE_CAPACITY = {
    "motorcycle": 12,
    "scooter": 10,
    "bicycle": 6,
    "van": 30,
}

MEDICAL_CATEGORY_MAPPING = {
    "skincare": ("medicamentos_criticos", 2, 5),
    "cosmetics": ("medicamentos_criticos", 2, 5),
    "grocery": ("medicamentos_criticos", 2, 5),
    "home": ("insumos_medicos", 3, 4),
    "kitchen": ("insumos_medicos", 3, 4),
    "pet supplies": ("insumos_medicos", 3, 4),
    "outdoors": ("insumos_medicos", 3, 4),
}


def convert_amazon_csv(path: str | Path) -> dict[str, list[dict[str, str]]]:
    rows = _read_rows(path)
    if not rows:
        raise ValueError("Amazon dataset is empty.")

    medical_rows = [row for row in rows if _medical_mapping(row) is not None]
    if not medical_rows:
        raise ValueError("Amazon dataset has no rows compatible with the medical mapping.")

    first_row = medical_rows[0]
    stops = [
        {
            "stop_id": "DEPOT-STORE",
            "name": "Store Depot",
            "x": first_row["Store_Latitude"],
            "y": first_row["Store_Longitude"],
            "demand": "0",
            "priority": "0",
            "is_depot": "true",
        }
    ]

    seen_vehicles = set()
    vehicles = []
    for row in medical_rows:
        mapped_name, demand, priority = _medical_mapping(row)
        stops.append(
            {
                "stop_id": row["Order_ID"],
                "name": mapped_name,
                "x": row["Drop_Latitude"],
                "y": row["Drop_Longitude"],
                "demand": str(demand),
                "priority": str(_priority_from_row(row, priority)),
                "is_depot": "false",
            }
        )

        vehicle_name = row["Vehicle"].strip()
        if vehicle_name in seen_vehicles:
            continue
        seen_vehicles.add(vehicle_name)
        vehicles.append(
            {
                "vehicle_id": vehicle_name,
                "capacity": str(VEHICLE_CAPACITY.get(vehicle_name.strip().lower(), 15)),
                "max_distance": str(_max_distance_from_vehicle(vehicle_name)),
            }
        )

    return {"stops": stops, "vehicles": vehicles}


def write_amazon_converted_csvs(input_path: str | Path, output_dir: str | Path) -> tuple[Path, Path]:
    converted = convert_amazon_csv(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stops_path = output_dir / "stops_from_amazon.csv"
    vehicles_path = output_dir / "vehicles_from_amazon.csv"
    _write_csv(stops_path, converted["stops"])
    _write_csv(vehicles_path, converted["vehicles"])
    return stops_path, vehicles_path


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS.difference(fieldnames)
        if missing:
            raise ValueError(f"Amazon dataset missing columns: {sorted(missing)}")
        if "Delivery_Category" not in fieldnames and "Category" not in fieldnames:
            raise ValueError("Amazon dataset missing category column: expected Delivery_Category or Category")
        return list(reader)


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _priority_from_row(row: dict[str, str], base_priority: int) -> int:
    traffic = row["Traffic"].strip().lower()
    weather = row["Weather"].strip().lower()
    priority = base_priority

    if traffic == "jam":
        priority = min(5, priority + 1)
    if weather in {"stormy", "fog"}:
        priority = min(5, priority + 1)
    return priority


def _category_value(row: dict[str, str]) -> str:
    return row.get("Delivery_Category") or row.get("Category") or "Unknown"


def _medical_mapping(row: dict[str, str]) -> tuple[str, int, int] | None:
    return MEDICAL_CATEGORY_MAPPING.get(_category_value(row).strip().lower())


def _max_distance_from_vehicle(vehicle_name: str) -> int:
    vehicle_name = vehicle_name.strip().lower()
    if vehicle_name == "bicycle":
        return 15
    if vehicle_name in {"motorcycle", "scooter"}:
        return 25
    if vehicle_name == "van":
        return 40
    return 30
