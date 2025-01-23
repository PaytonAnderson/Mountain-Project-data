'''
accumulator.py

Provides the accumulator class, which converts a paginated API, for example
themountainproject's rating and ticks APIs, into Python generators. This means
that writing code like

for i, rating in enumerate(accumulator.generator()):
    if i >= 10:
        break

    print(rating)

will print the first 10 ratings returned from the API. If the first request
send to the ratings API contains at least 10 ratings, only one request will be
sent. However, if more ratings are needed, the additional API call will be made
only when the generator goes that far. This, in general, makes quick iterations
faster.
'''

from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Accumulator:
    '''
    Class to manage lazy pagination. That is, allow iteration through a
    paginated API, e.g. ticks for a route, while only making additional API
    calls when additional data is needed.

    Fields:
        zero_indexed_fetcher: A function that given an integer i returns the
            ith page of data. The first page is index 0.
    '''

    zero_indexed_fetcher: Callable[[int], List]

    def generator(self):
        i = 0
        page = self.zero_indexed_fetcher(i)

        while len(page) > 0:
            yield from page
            i += 1
            page = self.zero_indexed_fetcher(i)
