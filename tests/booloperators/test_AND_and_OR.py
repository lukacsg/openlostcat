import unittest
from openlostcat.operators.bool_operators import BoolAND, BoolOR
from openlostcat.utils import to_tag_bundle_set
from tests.booloperators import test_operators_list


class TestAndOr(unittest.TestCase):

    def test_AND(self):
        validation = [False, False, True, False, False, False, True, False]
        for (test, valid) in list(zip(test_operators_list, validation)):
            self.assertEqual(
                BoolAND(test).apply(to_tag_bundle_set([]))[0], valid)

    def test_OR(self):
        validation = [True, True, True, False, True, True, True, False]
        for (test, valid) in list(zip(test_operators_list, validation)):
            self.assertEqual(
                BoolOR(test).apply(to_tag_bundle_set([]))[0], valid)


if __name__ == '__main__':
    unittest.main()
