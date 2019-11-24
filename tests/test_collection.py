import datetime
from unittest import TestCase

from compy.collection import Collection


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
