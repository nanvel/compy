from unittest import TestCase

from compy.outcome import Outcome


class OutcomeTestCase(TestCase):

    def test_outcome(self):
        outcome1 = Outcome(is_positive=True, is_hard=True)
        outcome2 = Outcome(is_positive=True, is_hard=True)
        outcome3 = Outcome(is_positive=True, is_hard=False)
        self.assertEqual(str(outcome1), "hard positive")
        self.assertEqual(outcome1, outcome2)
        self.assertNotEqual(outcome1, outcome3)

        outcome4 = Outcome(is_positive=None, is_hard=None)
