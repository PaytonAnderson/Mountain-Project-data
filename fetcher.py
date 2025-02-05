'''
fetcher.py

Provides some functions that call themountainproject APIs and convert their
relatively wild JSON responses into controlled dataclasses that are
IDE-friendly.
'''

import json
import re
import requests
import sys
from datetime import datetime
from typing import Generator, List

from model import Area, Route, RouteRating, RouteTick

# Constants related to themountainproject's API
MTN_PROJECT_API = 'https://www.mountainproject.com/api/v2'
MTN_PROJECT_ROOT = 'https://www.mountainproject.com'
PAGE_SIZE = 250

# Constants related to how text is formatted in the API responses
AREA_HIERARCHY_PATTERN = re.compile(r'<script type="application/ld\+json">(.+?)</script>', re.DOTALL)
GENERIC_SITEMAP_URL_PATTERN = re.compile(r'<loc>(.*?)</loc>')
GPS_PATTERN = re.compile(r'<td>GPS:</td>\s*<td>\s*(-?\d+\.\d+), (-?\d+\.\d+)')
SITEMAP_AREA_PATTERN = re.compile(r'https://www.mountainproject.com/area/(\d+)/([^/<]+)')
SITEMAP_ROUTE_PATTERN = re.compile(r'<loc>https://www.mountainproject.com/route/(\d+)/([^/]+)</loc>')
TICK_DATE_FORMAT = '%b %d, %Y, %I:%M %p'


def safe_run(callable):
    try:
        return callable()
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        print(e, file=sys.stderr)
    except:
        pass

    return None


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


def parse_breadcrumb(dictionary) -> int:
    '''
    Return the area_id from an area url
    '''

    position = dictionary['position']
    if position == 1:
        return 0

    return int(SITEMAP_AREA_PATTERN.match(dictionary['item']).group(1))


def fetch_area(area_url: str) -> Area:
    area_id, area_short_name = [cons(x)
                                for cons, x
                                in zip([int, str],
                                       SITEMAP_AREA_PATTERN.match(area_url)
                                            .group(1, 2))]

    area_xml_request = requests.get(area_url)

    area_xml_request.raise_for_status()
    xml = area_xml_request.text

    gps_matches = GPS_PATTERN.findall(xml)
    assert len(gps_matches) == 1, 'Wrong number of GPS matches (%d)' % len(gps_matches)
    longitude, latitude = map(float, gps_matches[0])

    area_hierarchy_matches = AREA_HIERARCHY_PATTERN.findall(xml)

    hierarchy = None
    if len(area_hierarchy_matches) == 0:
        hierarchy = [area_id, 0]
    else:
        match json.loads(area_hierarchy_matches[0]):
            case {'itemListElement': [*breadcrumbs]}:
                hierarchy = [parse_breadcrumb(breadcrumb)
                             for breadcrumb in breadcrumbs[::-1]]
            case other:
                raise Exception("Could not parse hierarchy " + str(other))

    return Area(area_id, area_short_name, latitude, longitude, hierarchy)


def fetch_areas(i: int) -> Generator[Area, None, None]:
    '''
    Fetch the ith page of areas.
    '''

    page_request = requests.get('{}/sitemap-areas-{}.xml'
                                .format(MTN_PROJECT_ROOT, i))

    page_request.raise_for_status()
    xml = page_request.text

    urls = GENERIC_SITEMAP_URL_PATTERN.findall(xml)

    areas = (safe_run(lambda: fetch_area(url)) for url in urls)

    return (area for area in areas if area is not None)


def fetch_routes(i: int) -> List[Route]:
    '''
    Fetch the ith page of routes.
    '''

    page_request = requests.get('{}/sitemap-routes-{}.xml'
                                .format(MTN_PROJECT_ROOT, i))

    page_request.raise_for_status()
    xml = page_request.text

    return [Route(id, name) for id, name in SITEMAP_ROUTE_PATTERN.findall(xml)]


if __name__ == '__main__':
    for area in fetch_areas(0):
        print(area)
