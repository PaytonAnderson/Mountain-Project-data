import random
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass
from sqlite3 import Cursor
from typing import Callable, List, Literal, Optional, Union

from collaborative_filtering import get_recommendations_to_list as collab_filtering


class SourceOfTruth:
    cursor: Cursor

    def __init__(self, db_path):
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        self.cursor = conn.cursor()

    def is_good_recommendation(
      self, user_id: int, route_id: int) -> Optional[Union[Literal['YES'], Literal['NO']]]:
        '''
        Return YES if the user left a positive review, NO if the user left a
        negative review, or None if the user has not left a review.
        '''

        cursor.execute('''SELECT score FROM reviews
                       WHERE 1=1
                       AND user_id = ?
                       AND route_id = ?;''', [user_id, route_id])

        result = cursor.fetchone()
        if result:
            print(f'Result: user {user_id} said {result[0]} on recommendation for {route_id}')
            return 'YES' if result[0] >= 3 else 'NO'

        return None


@dataclass(frozen=True)
class TestResultEvaluation:
    pass


@dataclass(frozen=True)
class TestScorer:
    source_of_truth: SourceOfTruth

    def assess_results(self, user_id: int, results: List[int]) -> TestResultEvaluation:
        result_count_by_assessment = defaultdict(int)
        for route_id in results:
            result_count_by_assessment[
                self.source_of_truth.is_good_recommendation(
                    user_id, route_id)] += 1

        print(user_id, result_count_by_assessment)


@dataclass
class UserTest:
    user_id: int
    db_path: str


@dataclass
class TestedAlgorithm:
    scorer: TestScorer

    implementation: Callable[[int, str], List[int]]
    '''
    A function that takes a user_id and a db_path and returns a list of
    recommended route_id.
    '''

    def apply(self, test: UserTest) -> TestResultEvaluation:
        results = self.implementation(test.user_id, test.db_path)
        return self.scorer.assess_results(test.user_id, results)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} test_db_path num_tests', file=sys.stderr)
        exit(1)

    # Full database used for determining if recommendations were good or not
    source_of_truth_path = 'databasev2.db'

    db_path = sys.argv[1]
    num_tests = int(sys.argv[2])

    # Connect in read-only mode, our algorithms should not be writing
    conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    cursor = conn.cursor()

    source_of_truth = SourceOfTruth(source_of_truth_path)
    scorer = TestScorer(source_of_truth)
    algorithms = (
        TestedAlgorithm(scorer, collab_filtering),
    )

    cursor.execute('''SELECT user_id FROM reviews;''')

    user_ids = [x[0] for x in cursor.fetchall()]

    test_user_ids = [random.choice(user_ids) for _ in range(num_tests)]

    for test_user_id in test_user_ids:
        for alg in algorithms:
            alg.apply(UserTest(test_user_id, db_path))
