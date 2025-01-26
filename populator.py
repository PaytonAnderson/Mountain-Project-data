'''
Accept the output of scraper.py in stdin. Populate the SQLite file passed as a
command line argument, or populate mydatabase.db if no arg is given.

Usage with compressed data (default to mydatabase.db):
bzcat data.bz2 | python3 populator.py
'''

import dateutil.parser
import json
import sqlite3
import sys
from sqlite3 import Connection, Cursor

from typing import Generator, Union

from model import Route, RouteRating, RouteTick


def connect(file_name: str) -> Connection:
    return sqlite3.connect(file_name)


def generate_entities(input_file = sys.stdin) -> Generator[
        Union[Route, RouteRating, RouteTick], None, None]:
    for line in input_file.read().splitlines():
        data = json.loads(line)

        entity = None
        match data:
            case {'routeId': rid, 'routeName': rname}:
                entity = Route(rid, rname)
            case {'routeId': rid, 'userId': uid, 'ratings': [*ratings]}:
                entity = RouteRating(rid, uid, ratings)
            case {'routeId': rid, 'userId': uid, 'text': text, 'date': date}:
                entity = RouteTick(rid, uid, text,
                                   dateutil.parser.isoparse(date))

        yield entity


def insert_entity(cursor: Cursor, item: Union[Route, RouteRating, RouteTick]):
    match item:
        case Route(rid, rname):
            cursor.execute('INSERT INTO routes (id, name) VALUES (?, ?)',
                           [rid, rname])
        case RouteRating(rid, uid, [*ratings]):
            for rating in ratings:
                cursor.execute('INSERT INTO ratings (route_id, user_id, rating) VALUES (?, ?, ?)',
                               [rid, uid, rating])
        case RouteTick(rid, uid, text, date):
            cursor.execute('INSERT INTO ticks (route_id, user_id, `text`, `date`) VALUES (?, ?, ?, ?)',
                           [rid, uid, text, date.isoformat()])


if __name__ == '__main__':
    file_name = 'mydatabase.db' if len(sys.argv) == 1 else sys.argv[1]
    conn = connect(file_name)
    cursor = conn.cursor()

    for entity in generate_entities():
        insert_entity(cursor, entity)

    conn.commit()
    conn.close()
