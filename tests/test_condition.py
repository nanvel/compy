from unittest import TestCase

from compy.condition import evaluate_condition
from compy.context import Context
from compy.outcome import NEGATIVE_SOFT, POSITIVE_HARD


class ConditionTestCase(TestCase):

    def test_evaluate_condition(self):
        context = Context(conf={
            'a': {
                'type': 'int',
                'initial': 10,
                'can_decrease': False
            },
            'b': {
                'type': 'int'
            }
        })

        outcome, ctx_keys = evaluate_condition('a_gt', value='100', ctx=context)
        self.assertEqual(outcome, NEGATIVE_SOFT)
        self.assertEqual(ctx_keys, ('a',))
        context.update('a', 200)
        outcome, ctx_keys = evaluate_condition('a_gt', value='100', ctx=context)
        self.assertEqual(outcome, POSITIVE_HARD)
        self.assertEqual(ctx_keys, ('a',))
        outcome, ctx_keys = evaluate_condition('a_gt', value='8+20', ctx=context)
        self.assertEqual(outcome, POSITIVE_HARD)
        self.assertEqual(ctx_keys, ('a',))
        outcome, ctx_keys = evaluate_condition('b_lte', value='0', ctx=context)
        self.assertEqual(outcome, None)
        self.assertEqual(ctx_keys, ('b',))
        outcome, ctx_keys = evaluate_condition('a_lte', value='$b', ctx=context)
        self.assertEqual(outcome, None)
        self.assertEqual(ctx_keys, ('a', 'b'))
