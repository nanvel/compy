# Smart conditions matching

1. `now > datetime.datetime(2000, 1, 1)`
this condition now should always be True

2. `const_false_var AND another_var`
will always be false

Count 1 as HARD_POSITIVE and 2 as HARD_NEGATIVE.
There are more cases when we can find the condition has no chances to change in future.
Conditions those can change are SOFT_POSITIVE and SOFT_NEGATIVE.

## Structure

There are context and groups of conditions, those are grouped into collections.
Groups ca refer each other outcome inside collections.

## Example

```python
import datetime
from unittest import TestCase

from compy import Collection


class CollectionTestCase(TestCase):

    def test_collection(self):
        collection = Collection(conf={
            'context': {
                'a': {
                    'type': 'int'
                },
                'now': {
                    'type': 'datetime',
                    'can_decrease': False
                }
            },
            'groups': [{
                'name': 'g1',
                'conf': {
                    'a_gt': 10
                },
                'lock_on_true': True
            }, {
                'name': 'g2',
                'conf': {
                    'group_g1_eq': True,
                    'group_g1:ts_lt': '$now-1m'
                }
            }]
        })

        outcomes = collection.evaluate(updates={})
        self.assertEqual(outcomes, {'g1': None, 'g2': None})
        self.assertEqual(collection.context_watching, {'group_g1', 'a', 'now'})
        now = datetime.datetime.utcnow()
        outcomes = collection.evaluate(updates={'now': now, 'a': 11})
        self.assertEqual(collection.context_watching, {'group_g1', 'a', 'now'})
        self.assertTrue(outcomes['g1'].is_positive)
        self.assertFalse(outcomes['g1'].is_hard)
        self.assertFalse(outcomes['g2'].is_positive)
        self.assertFalse(outcomes['g2'].is_hard)
        outcomes = collection.evaluate(updates={'now': now + datetime.timedelta(minutes=5)})
        self.assertEqual(collection.context_watching, {'a'})
        self.assertTrue(outcomes['g2'].is_positive)
        self.assertTrue(outcomes['g2'].is_hard)
```
