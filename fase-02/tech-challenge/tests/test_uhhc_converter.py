from pathlib import Path

from medical_route_optimizer.uhhc_converter import convert_uhhc_instance


def test_convert_uhhc_instance_creates_stops_and_vehicle_rows():
    dataset_dir = Path(__file__).resolve().parents[1] / "dataset"
    converted = convert_uhhc_instance(dataset_dir / "public" / "uhhc_A1.json")

    assert converted["stops"][0]["is_depot"] == "true"
    assert converted["stops"][1]["stop_id"].startswith("p")
    assert converted["stops"][1]["priority"] in {"3", "4", "5"}
    assert converted["vehicles"][0]["vehicle_id"] == "c1"
    assert len(converted["stops"]) == 11
    assert len(converted["vehicles"]) == 3
