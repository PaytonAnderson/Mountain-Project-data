'''
fetcher.py

Provides some functions that call themountainproject APIs and convert their
relatively wild JSON responses into controlled dataclasses that are
IDE-friendly.
'''

import re
import requests
from datetime import datetime
from typing import List

from model import Route, RouteRating, RouteTick

# Constants related to themountainproject's API
MTN_PROJECT_API = 'https://www.mountainproject.com/api/v2'
MTN_PROJECT_ROOT = 'https://www.mountainproject.com'
PAGE_SIZE = 250

# Constants related to how text is formatted in the API responses
SITEMAP_ROUTE_PATTERN = re.compile(r'<loc>https://www.mountainproject.com/route/(\d+)/([^/]+)</loc>')
TICK_DATE_FORMAT = '%b %d, %Y, %I:%M %p'


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
                parsed_date = datetime(1970, 1, 1, 0, 0, 0)
                try:
                    parsed_date = datetime.strptime(
                        datestring, TICK_DATE_FORMAT)
                except:
                    pass

                result.append(RouteTick(route_id, uid, text, parsed_date))
            case _:
                pass

    return result


def fetch_routes(i: int) -> List[Route]:
    '''
    Fetch the ith page of routes.
    '''

    page_request = requests.get('{}/sitemap-routes-{}.xml'
                                .format(MTN_PROJECT_ROOT, i))

    page_request.raise_for_status()
    xml = page_request.text

    return [Route(id, name) for id, name in SITEMAP_ROUTE_PATTERN.findall(xml)]
