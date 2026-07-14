from dataclasses import dataclass


@dataclass(frozen=True)
class Stop:
    stop_id: str
    name: str
    x: float
    y: float
    demand: int
    priority: int
    is_depot: bool = False


@dataclass(frozen=True)
class Vehicle:
    vehicle_id: str
    capacity: int
    max_distance: float


@dataclass(frozen=True)
class VehicleRoute:
    vehicle_id: str
    stop_ids: list[str]
    distance: float
    load: int
    capacity_overflow: int
    distance_overflow: float


@dataclass(frozen=True)
class OptimizationResult:
    routes: list[VehicleRoute]
    best_sequence: list[str]
    best_fitness: float
    total_distance: float
    history: list[float]
