import json
from dataclasses import dataclass
from typing import List

import requests


MTN_PROJECT_ROOT = 'https://www.mountainproject.com'


class RatingsAccumulator:
    def __init__(self):
        self.ratings = []

    def accumulate(self, text) -> bool:
        '''
        Iterate over the objects in the JSON formatted text. Return True if any
        ratings were found in the text, False otherwise.
        '''
        prev_len = len(self.ratings)
        json.loads(text, object_hook=self._accumulate)
        return len(self.ratings) > prev_len

    def _accumulate(self, obj):
        match obj:
            case {'id': _, 'allRatings': _}:
                self.ratings.append(obj)
            case _:
                pass

    def pprint(self):
        for rating in self.ratings:
            print(f'{rating["id"]} said {rating["allRatings"]}')

    def __repr__(self):
        return json.dumps(self.ratings)


@dataclass
class RouteRating:
    route_id: int
    user_id: int
    ratings: List[str]


@dataclass
class Route:
    id: int
    name: str

    def get_ratings(self) -> List[RouteRating]:
        url = f'{MTN_PROJECT_ROOT}/api/v2/routes/{self.id}/ratings'
        ratings_raw_req = requests.get(url)
        ratings_raw_req.raise_for_status()
        ratings_raw = ratings_raw_req.text

        accumulator = RatingsAccumulator()
        accumulator.accumulate(ratings_raw)
        accumulator.pprint()

        return accumulator


if __name__ == '__main__':
    route = Route(105862930, 'central-pillar-of-frenzy')
    route.get_ratings()
