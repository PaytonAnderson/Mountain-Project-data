'''
Takes a sqlite dump of a database in stdin and output the dump of a smaller
database in sqlite. This is done by maintaining all schema commands while
discarding some insert statements.

Initially, this script is going to be used to test our collaborative filtering
algorithms. Because our algorithms operate on ratings data, we will keep all
routes while discarding some amount of ratings and discarding all 
'''

import random
import re
import sys
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass
class SqlDumpLineHandler:
    '''
    Captures a handler that takes a line of SQL dump
    '''
    does_line_match: Callable[[str], bool]
    line_handler: Callable[[str], None]
    name: str
    counter: int = 0

    def handle_line(self, line: str) -> bool:
        '''
        Take a line and, if the does_line_match predicate returns True, run
        the line_handler and return True. Return False otherwise.
        '''

        if self.does_line_match(line):
            self.line_handler(line)
            self.counter += 1
            return True

        return False

    def __repr__(self):
        return f'{self.name} caught {self.counter:,} times'


DROP_REVIEW_CHANCE = float(sys.argv[1])
INSERT_INTO_ROUTES = re.compile(r'^INSERT INTO routes.*?;$')
INSERT_INTO_REVIEWS = re.compile(r'^INSERT INTO reviews.*?;$')
INSERT_INTO_OTHER = re.compile(r'^INSERT INTO (areas|ratings|ticks).*?;$')


PRINT_STRIPPED: Callable[[str], None] = lambda x: print(x.strip())


def randomly_drop_lines(line: str):
    roll = random.random()

    if roll < DROP_REVIEW_CHANCE:
        return

    PRINT_STRIPPED(line)


HANDLER_CHAIN = (
    SqlDumpLineHandler(lambda x: INSERT_INTO_ROUTES.match(x) is not None,
                       PRINT_STRIPPED, 'INSERT ROUTE'),
    SqlDumpLineHandler(lambda x: INSERT_INTO_REVIEWS.match(x) is not None,
                       randomly_drop_lines, 'INSERT REVIEW'),
    SqlDumpLineHandler(lambda x: INSERT_INTO_OTHER.match(x) is not None,
                       lambda _: None, 'INSERT OTHER'),
    SqlDumpLineHandler(lambda _: True, PRINT_STRIPPED, 'OTHER')
)


def execute_handler_chain(chain: Iterable[SqlDumpLineHandler], line: str):
    for handler in chain:
        if handler.handle_line(line):
            return

    raise ValueError('No chain matched for ' + line)


if __name__ == '__main__':
    for line in sys.stdin:
        execute_handler_chain(HANDLER_CHAIN, line)

    for handler in HANDLER_CHAIN:
        print(handler, file=sys.stderr)
