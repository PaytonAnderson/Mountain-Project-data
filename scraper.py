'''
Scrapes mountainproject.com and outputs data in the following format:

area:
{
    "area_id": 0,
    "area_name": "",
    "latitude": -180.00000,
    "longitude": -180.00000,
    "area_chain": [0]
}

route:
{
    "routeId": "0",
    "routeName": ""
}

rating:
{
    "routeId": "0",
    "userId": 0,
    "ratings": [""]
}

tick:
{
    "routeId": "0",
    "userId": 0,
    "text": "",
    "date": "YYYY-MM-DDThh-mm-ss" (Date.isoformat())
}

review:
{
    "route_id": "0",
    "user_id": 0,
    "score": 0
}
'''

import json
import sys
from dataclasses import asdict
from typing import Optional

import fetcher
from accumulator import Accumulator as Acc
from model import Route, RouteRating, RouteTick

ITERATIVE_MILESTONE = 100


def stringify_entity(entity) -> Optional[str]:
    dictionary = None
    match entity:
        case Route(rid, rname):
            dictionary = {'routeId': rid, 'routeName': rname}
        case RouteRating(rid, uid, ratings):
            dictionary = {'routeId': rid, 'userId': uid, 'ratings': ratings}
        case RouteTick(rid, uid, text, date):
            dictionary = {
                'routeId': rid,
                'userId': uid,
                'text': text,
                'date': date.isoformat()
                }
        case other:
            try:
                return json.dumps(asdict(other))
            except:
                print('ERROR: Unexpected entity %s' % str(other),
                      file=sys.stderr)
                return None

    return json.dumps(dictionary)


def print_entity(entity):
    stringified = stringify_entity(entity)
    if stringified is not None:
        print(stringify_entity(entity))


def handle_route(route: Route):
    print_entity(route)

    ratings_accumulator = Acc(lambda i: fetcher.fetch_ratings(i, route.id))
    ticks_accumulator = Acc(lambda i: fetcher.fetch_ticks(i, route.id))
    reviews_accumulator = Acc(lambda i: fetcher.fetch_reviews(i, route.id))

    for rating in ratings_accumulator.generator():
        print_entity(rating)

    for tick in ticks_accumulator.generator():
        print_entity(tick)

    for review in reviews_accumulator.generator():
        print_entity(review)


def scrape():
    sitemap = fetcher.get_sitemap()

    area_count = 0
    area_pages = fetcher.SITEMAP_AREA_PAGE_PATTERN.findall(sitemap)
    for area_page in area_pages:
        for area in fetcher.fetch_areas(area_page):
            if area_count % ITERATIVE_MILESTONE == 0:
                print(f'areas[{area_count}]', file=sys.stderr)

            print(json.dumps(asdict(area)))
            area_count += 1

    routes_accumulator = Acc(lambda i: fetcher.fetch_routes(i))
    for i, route in enumerate(routes_accumulator.generator()):
        if i % 100 == 0:
            print(f'routes[{i}]', file=sys.stderr)

        handle_route(route)


if __name__ == '__main__':
    scrape()
