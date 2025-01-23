from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Route:
    id: int
    name: str


@dataclass
class RouteRating:
    route_id: int
    user_id: int
    ratings: List[str]


@dataclass
class RouteTick:
    route_id: int
    user_id: int
    text: str
    date: datetime
