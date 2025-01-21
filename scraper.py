import json
from typing import List

import requests

from model import Route, RouteRating, RouteTick


MTN_PROJECT_ROOT = 'https://www.mountainproject.com'


class TicksAccumulator:
    route: Route
    ticks: List[RouteTick]
    base_url: str
    current_page: int
    page_size: int

    def __init__(self, route: Route):
        self.route = route
        self.ticks = []
        self.base_url = f'{MTN_PROJECT_ROOT}/api/v2/routes/{route.id}/ticks'
        self.current_page = 1
        self.page_size = 250

    def accumulate(self) -> bool:
        '''
        Iterate over the objects in the JSON formatted text. Return True if any
        ticks were found, False otherwise.
        '''
        ticks_req = requests.get('{}?per_page={}&page={}'
                                   .format(self.base_url, self.page_size,
                                           self.current_page))

        ticks_req.raise_for_status()
        text = ticks_req.text
        self.current_page += 1

        prev_len = len(self.ticks)

        json.loads(text, object_hook=self._accumulate)

        return len(self.ticks) > prev_len

    def _accumulate(self, obj):
        match obj:
            case {'id': _, 'user': {'id': uid}}:
                print(obj)
                self.ticks.append(RouteTick(self.route.id, uid))
            case _:
                pass

        return obj

    def pprint(self):
        for tick in self.ticks:
            print(f'{tick.user_id}')

    def __repr__(self):
        return json.dumps(self.ratings)


class RatingsAccumulator:
    '''
    Class to accumulate all the ratings users have left for a route. Call
    accumulate until it returns False to collect all the ratings.
    '''
    ratings: List[RouteRating]
    base_url: str
    current_page: int
    page_size: int

    def __init__(self, route: Route):
        self.ratings = []
        self.base_url = f'{MTN_PROJECT_ROOT}/api/v2/routes/{route.id}/ratings'
        self.current_page = 1
        self.page_size = 250

    def accumulate(self) -> bool:
        '''
        Iterate over the objects in the JSON formatted text. Return True if any
        ratings were found in the text, False otherwise.
        '''
        ratings_req = requests.get('{}?per_page={}&page={}'
                                   .format(self.base_url, self.page_size,
                                           self.current_page))

        ratings_req.raise_for_status()
        text = ratings_req.text
        self.current_page += 1

        prev_len = len(self.ratings)

        json.loads(text, object_hook=self._accumulate)

        return len(self.ratings) > prev_len

    def _accumulate(self, obj):
        match obj:
            case {'id': uid, 'allRatings': ratings}:
                self.ratings.append(RouteRating(None, uid, ratings))
            case _:
                pass

    def pprint(self):
        for rating in self.ratings:
            print(f'{rating.user_id} said {rating.ratings}')

    def __repr__(self):
        return json.dumps(self.ratings)


def get_ratings(route: Route) -> List[RouteRating]:
    # or RatingsAccumulator to print out people's suggested ratings for a route
    accumulator = TicksAccumulator(route)
    while accumulator.accumulate():
        pass

    accumulator.pprint()

    return accumulator


if __name__ == '__main__':
    # The Ratings and Ticks accumulators only actually use the numeric id
    route = Route(105862930, 'central-pillar-of-frenzy')
    get_ratings(route)
