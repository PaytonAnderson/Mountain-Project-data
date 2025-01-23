'''
fetcher.py

Provides some functions that call themountainproject APIs and convert their
relatively wild JSON responses into controlled dataclasses that are
IDE-friendly.
'''

from datetime import datetime
import requests
from typing import Callable, List

from model import RouteRating, RouteTick

# Constants related to themountainproject's API
TICK_DATE_FORMAT = '%b %d, %Y, %I:%M %p'
MTN_PROJECT_API = 'https://www.mountainproject.com/api/v2'
PAGE_SIZE = 250


def fetch_ratings(i: int, route_id: int) -> List[RouteRating]:
    '''
    Fetch the ith page of user suggested ratings for some route.
    '''

    page_request = requests.get('{}/routes/{}/ratings?per_page={}&page={}'
                                .format(MTN_PROJECT_API, route_id, PAGE_SIZE,
                                        i + 1))

    page_request.raise_for_status()

    data = page_request.json()
    result = []
    for obj in data['data']:
        match obj:
            case {'allRatings': [*ratings], 'user': {'id': uid}}:
                result.append(RouteRating(route_id, uid, ratings))
            case _:
                pass

    return result


def fetch_ticks(i: int, route_id: int) -> List[RouteTick]:
    '''
    Fetch the ith page of ticks for some route.
    '''

    page_request = requests.get('{}/routes/{}/ticks?per_page={}&page={}'
                                .format(MTN_PROJECT_API, route_id, PAGE_SIZE,
                                        i + 1))

    page_request.raise_for_status()
    data = page_request.json()
    result = []
    for obj in data['data']:
        match obj:
            case {'date': datestring, 'text': text, 'user': {'id': uid}}:
                parsed_date = datetime.strptime(datestring, TICK_DATE_FORMAT)
                result.append(RouteTick(route_id, uid, text, parsed_date))
            case _:
                pass

    return result
