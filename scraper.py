import json
import sys

import fetcher
from accumulator import Accumulator as Acc
from model import Route, RouteRating, RouteTick


def stringify_entity(entity) -> str:
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
            raise ValueError('Unexpected entity %s' % str(entity))

    return json.dumps(dictionary)


def print_entity(entity):
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
    routes_accumulator = Acc(lambda i: fetcher.fetch_routes(i))
    for route in routes_accumulator.generator():
        print(route, file=sys.stderr)
        handle_route(route)


if __name__ == '__main__':
    scrape()
