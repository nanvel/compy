from unittest import TestCase

from compy.context import Context
from compy.group import Group
from compy.outcome import NEGATIVE_SOFT, NEGATIVE_HARD


class GroupTestCase(TestCase):

    def test_group(self):
        context = Context(conf={
            'a': {
                'type': 'int',
                'initial': 1
            },
            'b': {
                'type': 'int',
                'initial': 2
            },
            'c': {
                'type': 'int',
                'initial': 150,
                'can_increase': False
            },
        })
        group = Group(
            name='g1',
            conf={
                'a_gt': '$b',
                'c_gt': 100
            }
        )
        outcome = group.evaluate(ctx=context)
        self.assertEqual(outcome, NEGATIVE_SOFT)
        self.assertEqual(group.context_watching, {'a', 'b', 'c'})
        context.update('c', 90)
        outcome = group.evaluate(ctx=context)
        self.assertEqual(group.context_watching, set())
        self.assertEqual(outcome, NEGATIVE_HARD)
