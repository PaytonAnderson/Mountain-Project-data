'''
Converts model classes to and from json strings.
'''

import json
import sys
from datetime import datetime
from typing import Any, Callable, Generator, Optional, TextIO, Union

from model import Area, Route, RouteRating, RouteReview, RouteTick


class SafeCaster:
    '''
    Utility class to manage casting. Each instance of the class keeps track of
    how many exceptions it has swallowed.
    '''

    error_count: int

    def __init__(self):
        self.error_count = 0

    def safe_cast(self, caster: Callable[[Any], Any], castee: Any) -> Optional[Any]:
        try:
            return caster(castee)
        except ValueError as e:
            print('SafeCaster failed with %s' % (e), file=sys.stderr)
            self.error_count += 1
            return None

    def get_error_count(self) -> int:
        return self.error_count


def from_json_string(json_string: str) -> (
  Optional[Union[Area, Route, RouteRating, RouteReview, RouteTick]]):
    obj = None
    try:
        obj = json.loads(json_string)
    except:
        return None

    result = None
    caster = SafeCaster()
    match obj:
        case {"routeId": str(route_id), "routeName": route_name}:
            # route case
            result = Route(caster.safe_cast(int, route_id), route_name, 0)
        case {"routeId": str(route_id),
              "userId": int(user_id),
              "ratings": [*ratings]}:
            # rating case
            result = RouteRating(caster.safe_cast(int, route_id),
                               user_id, ratings)
        case {"routeId": str(route_id),
              "userId": int(user_id),
              "text": str(text),
              "date": datestring}:
            # tick case
            result = RouteTick(caster.safe_cast(int, route_id),
                             user_id, text,
                             caster.safe_cast(datetime.fromisoformat,
                                              datestring))
        case {"route_id": str(route_id),
              "user_id": int(user_id),
              "score": int(score)}:
            # review case
            result = RouteReview(caster.safe_cast(int, route_id),
                               user_id, score)
        case {"area_id": int(area_id),
              "area_name": str(area_name),
              "latitude": float(latitude),
              "longitude": float(longitude),
              "area_chain": [*areas]}:
            # area case
            result = Area(area_id, area_name, latitude, longitude,
                        [caster.safe_cast(int, x) for x in areas])
        case _:
            print('Unexpected json object %s' % (obj), file=sys.stderr)
            return None

    return result if caster.get_error_count() == 0 else None


def from_jsonl(file: TextIO) -> Generator[
  Union[Area, Route, RouteRating, RouteReview, RouteTick], None, None]:
    for line in file:
        object = from_json_string(line)

        if object is not None:
            yield object


if __name__ == '__main__':
    for object in from_jsonl(sys.stdin):
        if isinstance(object, Area):
            print(object)
