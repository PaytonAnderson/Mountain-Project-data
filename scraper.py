import json
import sys
from dataclasses import asdict
from typing import Optional

import fetcher
from accumulator import Accumulator as Acc
from model import Area, Route, RouteRating, RouteTick

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
        case _:
            print('ERROR: Unexpected entity %s' % str(entity), file=sys.stderr)
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

    for rating in ratings_accumulator.generator():
        print_entity(rating)

    for tick in ticks_accumulator.generator():
        print_entity(tick)


def scrape():
    sitemap = fetcher.get_sitemap()

    # area_count = 0
    # area_pages = fetcher.SITEMAP_AREA_PAGE_PATTERN.findall(sitemap)
    # for area_page in area_pages:
    #     for area in fetcher.fetch_areas(area_page):
    #         if area_count % ITERATIVE_MILESTONE == 0:
    #             print(f'areas[{area_count}]', file=sys.stderr)

    #         print(json.dumps(asdict(area)))
    #         area_count += 1

    routes_accumulator = Acc(lambda i: fetcher.fetch_routes(i))
    for i, route in enumerate(routes_accumulator.generator()):
        if i % 100 == 0:
            print(f'routes[{i}]', file=sys.stderr)

        handle_route(route)


if __name__ == '__main__':
    scrape()
