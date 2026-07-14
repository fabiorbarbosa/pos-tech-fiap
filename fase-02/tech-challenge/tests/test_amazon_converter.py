from pathlib import Path

from medical_route_optimizer.amazon_converter import convert_amazon_csv


def test_convert_amazon_csv_creates_stops_and_vehicles():
    dataset_dir = Path(__file__).resolve().parents[1] / "dataset"
    converted = convert_amazon_csv(dataset_dir / "public" / "amazon_delivery_sample.csv")

    assert converted["stops"][0]["is_depot"] == "true"
    assert converted["stops"][1]["stop_id"] == "ORD-001"
    assert converted["stops"][1]["name"] == "medicamentos_criticos"
    assert converted["stops"][1]["priority"] == "5"
    assert converted["stops"][2]["priority"] == "5"
    assert converted["stops"][2]["name"] == "insumos_medicos"
    assert {row["vehicle_id"] for row in converted["vehicles"]} == {"Motorcycle", "Van"}
    assert len(converted["stops"]) == 3


def test_convert_amazon_csv_groups_by_vehicle():
    dataset_dir = Path(__file__).resolve().parents[1] / "dataset"
    converted = convert_amazon_csv(dataset_dir / "public" / "amazon_delivery_sample.csv")

    vehicles = {row["vehicle_id"]: row for row in converted["vehicles"]}

    assert vehicles["Motorcycle"]["capacity"] == "12"
    assert vehicles["Van"]["capacity"] == "30"


def test_convert_amazon_csv_filters_non_medical_categories():
    dataset_dir = Path(__file__).resolve().parents[1] / "dataset"
    converted = convert_amazon_csv(dataset_dir / "public" / "amazon_delivery_sample.csv")

    stop_ids = [row["stop_id"] for row in converted["stops"]]

    assert "ORD-003" not in stop_ids
    assert "Scooter" not in {row["vehicle_id"] for row in converted["vehicles"]}
