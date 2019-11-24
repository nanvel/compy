import datetime
from decimal import Decimal
from unittest import TestCase

from compy.context import Context
from compy.value import parse_value


context = Context(conf={
    'var1': {'type': 'bool'},
    'var2': {'type': 'int'},
    'var3': {'type': 'decimal'},
    'vart1': {
        'type': 'datetime',
        'initial': datetime.datetime(2019, 11, 23, 7, 45, 26),
        'can_increase': False
    },
    'vart2': {'type': 'datetime'}
})

context.update('var1', True)
context.variables['var1'].ts = datetime.datetime(2019, 6, 1)
context.update('var2', 1)
context.update('var3', Decimal('0.25'))
context.update('vart2', datetime.datetime(2019, 1, 1, 2, 2, 2))
context.update('vart1', datetime.datetime(2020, 1, 1))


TEST_CASE = [
    ('1', 'bool', (True, None)),
    ('1', 'decimal', (1, None)),
    ('$var1', 'bool', (True, 'var1')),
    ('1*2', 'decimal', (2, None)),
    ('1.2-2.5%', 'decimal', (Decimal('1.17'), None)),
    ('1*2', 'int', (2, None)),
    ('1+2', 'int', (3, None)),
    ('$vart1', 'datetime', (datetime.datetime(2019, 11, 23, 7, 45, 26), 'vart1')),
    ('$vart1+1d', 'datetime', (datetime.datetime(2019, 11, 24, 7, 45, 26), 'vart1')),
    ('$vart1-1d', 'datetime', (datetime.datetime(2019, 11, 22, 7, 45, 26), 'vart1')),
    ('$vart2+1s', 'datetime', (datetime.datetime(2019, 1, 1, 2, 2, 3), 'vart2')),
    ('$var1:ts', 'datetime', (datetime.datetime(2019, 6, 1), 'var1'))
]


class ValuesTestCase(TestCase):

    def test_parse_value(self):
        for v, vt, res in TEST_CASE:
            self.assertEqual(parse_value(v, vt, ctx=context), res)
