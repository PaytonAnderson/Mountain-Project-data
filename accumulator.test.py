import unittest

from accumulator import Accumulator


def raise_fetcher(x: int):
    match x:
        case 0:
            return [1, 2, 3]
        case 1:
            return [4, 5, 6]
        case 2:
            raise Exception


def quiet_fetcher(x: int):
    match x:
        case 0:
            return [1, 2, 3]
        case _:
            return []


class AccumulatorTest(unittest.TestCase):
    def test_pagination_with_exception_at_end(self):
        accumulator = Accumulator(raise_fetcher)
        generator = accumulator.generator()

        for i in range(6):
            self.assertEqual(i + 1, next(generator))

        self.assertRaises(Exception, lambda: next(generator))

    def test_pagination_with_safe_end(self):
        accumulator = Accumulator(quiet_fetcher)
        generator = accumulator.generator()
        self.assertListEqual([1, 2, 3], [x for x in generator])


if __name__ == '__main__':
    unittest.main()
