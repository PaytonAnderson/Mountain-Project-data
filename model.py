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


@dataclass
class Area:
    area_id: int
    area_name: str
    latitude: float
    longitude: float
    area_chain: List[int]
    '''
    Represents the hierarchy of the area. area_chain[0] is always equivalent to
    area_id, and area_chain[-1] is always 0, to indicate the root area that is
    not stored but recognized as a valid area.
    '''
