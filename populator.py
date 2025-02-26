'''
Accept the output of scraper.py in stdin. Populate the SQLite file passed as a
command line argument, or populate mydatabase.db if no arg is given.

Usage with compressed data (default to mydatabase.db):
bzcat data.bz2 | python3 populator.py

Expects the sqlite database to support the following tables:
CREATE TABLE areas (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
latitude DECIMAL(3,5) NOT NULL,
longitude DECIMAL(3,5) NOT NULL,
parent_id INTEGER);

CREATE TABLE ratings (
route_id INTEGER NOT NULL,
user_id INTEGER NOT NULL,
rating TEXT NOT NULL,
FOREIGN KEY (route_id) REFERENCES routes (id)
);

CREATE TABLE reviews (
route_id INTEGER NOT NULL,
user_id INTEGER NOT NULL,
score INTEGER NOT NULL,
FOREIGN KEY (route_id) REFERENCES routes (id)
);

CREATE TABLE routes (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
area_id INTEGER);

CREATE TABLE ticks (
route_id INTEGER NOT NULL,
user_id INTEGER NOT NULL,
`text` TEXT NOT NULL,
`date` TEXT NOT NULL,
FOREIGN KEY (route_id) REFERENCES routes (id)
);
'''

import re
import sqlite3
import sys
from collections import defaultdict
from sqlite3 import Connection, Cursor
from multiprocessing import Pool

from typing import Generator, Union

from fetcher import get_area_id_from_route_id
from model import Area, Route, RouteRating, RouteReview, RouteTick
from serializer import from_jsonl

DEFAULT_DATABASE_FILE_NAME = 'databasev2.db'


def connect(file_name: str) -> Connection:
    return sqlite3.connect(file_name)


def insert_entity(cursor: Cursor, item: Union[Route, RouteRating, RouteTick]):
    match item:
        case Route(rid, rname, area_id):
            cursor.execute('INSERT INTO routes (id, name, area_id) VALUES (?, ?, ?)',
                           [rid, rname, area_id])
        case RouteRating(rid, uid, [*ratings]):
            for rating in ratings:
                cursor.execute('INSERT INTO ratings (route_id, user_id, rating) VALUES (?, ?, ?)',
                               [rid, uid, rating])
        case RouteTick(rid, uid, text, date):
            cursor.execute('INSERT INTO ticks (route_id, user_id, `text`, `date`) VALUES (?, ?, ?, ?)',
                           [rid, uid, text, date.isoformat()])
        case RouteReview(rid, uid, score):
            cursor.execute('INSERT INTO reviews (route_id, user_id, score) VALUES (?, ?, ?)',
                           [rid, uid, score])
        case Area(aid, aname, lat, long, chain):
            cursor.execute('INSERT INTO areas (id, name, latitude, longitude, parent_id) VALUES (?, ?, ?, ?, ?)',
                           [aid, aname, lat, long, chain[1]])


def populate_db():
    file_name = (DEFAULT_DATABASE_FILE_NAME
                 if len(sys.argv) == 1
                 else sys.argv[1])

    conn = connect(file_name)
    cursor = conn.cursor()

    instances_by_exception = defaultdict(int)
    route_counter = 0

    for i, entity in enumerate(from_jsonl(sys.stdin)):
        if route_counter % 10_000 == 0 or i % 100_000 == 0:
            print('[%d:%d] %s' % (route_counter, i, type(entity)),
                  file=sys.stderr)

        if isinstance(entity, Route):
            route_counter += 1

        try:
            insert_entity(cursor, entity)
        except sqlite3.IntegrityError as e:
            instances_by_exception['sqlite3.IntegrityError'] += 1
            print(e, file=sys.stderr)
        except Exception as e:
            instances_by_exception['unknown'] += 1
            print(e, file=sys.stderr)

    print('Completed with exceptions %s' % instances_by_exception,
          file=sys.stderr)

    conn.commit()
    conn.close()


def print_route_with_area_id(row: int) -> None:
    route_id, route_name = row
    area_id = get_area_id_from_route_id(route_id, route_name, False)

    print(route_id, area_id, flush=True)
    print(route_id, area_id, file=sys.stderr)

    return (route_id, area_id)


def get_area_ids():
    file_name = (DEFAULT_DATABASE_FILE_NAME
                 if len(sys.argv) == 1
                 else sys.argv[1])

    conn = connect(file_name)
    cursor = conn.cursor()

    cursor.execute('SELECT id, name FROM routes WHERE area_id = 0 OR area_id IS NULL;')
    route_ids = cursor.fetchall()

    with Pool(4) as pool:
        pool.map(print_route_with_area_id, route_ids)


def update_area_ids():
    file_name = (DEFAULT_DATABASE_FILE_NAME
                 if len(sys.argv) == 1
                 else sys.argv[1])

    conn = connect(file_name)
    cursor = conn.cursor()

    pattern = re.compile(r'(\d+) (\d+)')
    stdin = sys.stdin.read()
    pairs = pattern.findall(stdin)

    i = 0
    for rid, aid in [map(int, x) for x in pairs]:
        print(rid, aid)
        cursor.execute('UPDATE routes SET area_id = ? WHERE id = ?',
                       [aid, rid])

        i += 1

        if i % 1_000 == 0:
            print(i)
            conn.commit()


if __name__ == '__main__':
    # get_area_ids()
    update_area_ids()
