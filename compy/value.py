import datetime
import re
from decimal import Decimal


class ValueParsingError(Exception):

    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class ValueParser:

    VAR_RE = re.compile(r'^\$([\w\:]+)')

    @classmethod
    def _from_context(cls, val, ctx):
        if not isinstance(val, str):
            return val, None
        if not val.startswith('$'):
            return val, None
        finds = cls.VAR_RE.search(val)
        if not finds:
            return val, None
        variable_name = finds.groups()[0]
        is_ts = False
        if variable_name.endswith(':ts'):
            variable_name = variable_name[:-3]
            is_ts = True
        if not ctx:
            raise ValueParsingError(f"Context required for {val}")
        if is_ts:
            return ctx.get(variable_name).ts, variable_name
        else:
            return ctx.get(variable_name).value, variable_name

    @classmethod
    def parse(cls, val, ctx):
        return cls._from_context(val=val, ctx=ctx)


class StrValueParser(ValueParser):

    @classmethod
    def parse(cls, val, ctx):
        val, context_used = super().parse(val=val, ctx=ctx)
        if val is None:
            return val, context_used
        if not isinstance(val, str):
            return str(val), context_used
        return val, context_used


class BoolValueParser(ValueParser):

    @classmethod
    def parse(cls, val, ctx):
        val, context_used = super().parse(val=val, ctx=ctx)
        if val is None:
            return val, context_used
        if isinstance(val, bool):
            return val, context_used
        elif isinstance(val, str):
            if val.lower() in ('true', 't', '1'):
                return True, context_used
            elif val.lower() in ('false', 'f', '0'):
                return False, context_used
        elif isinstance(val, int):
            if val == 1:
                return True, context_used
            elif val == 0:
                return False, context_used
        raise ValueParsingError(message=f"Can not parse {val}:bool")


class DecimalValueParser(ValueParser):

    PLUS_RE = re.compile(r'^(\$?[\w\.]+)([\+\-][\d\.]+)$')
    PLUS_PT_RE = re.compile(r'^(\$?[\w\.]+)([\+\-][\d\.]+)\%$')
    MULT_RE = re.compile(r'^(\$?[\w\.]+)\*([\d\.]+)$')

    @classmethod
    def _parse_modifier(cls, val):
        """
        *<int/decimal>
        +<decimal>
        -<decimal>
        +<decimal>%
        -<decimal>%
        """
        if not isinstance(val, str):
            return val, None, None

        if val.replace('.', '').isdigit():
            return val, None, None

        plus_res = cls.PLUS_RE.search(val)
        if plus_res:
            plus_res = plus_res.groups()
            return plus_res[0], Decimal(plus_res[1]), None

        plus_pt_res = cls.PLUS_PT_RE.search(val)
        if plus_pt_res:
            plus_pt_res = plus_pt_res.groups()
            return plus_pt_res[0], None, Decimal(plus_pt_res[1]) / 100 + 1

        mult_res = cls.MULT_RE.search(val)
        if mult_res:
            mult_res = mult_res.groups()
            return mult_res[0], None, Decimal(mult_res[1])

        return val, None, None

    @classmethod
    def parse(cls, val, ctx):
        val, plus_modifier, mult_modifier = cls._parse_modifier(val)
        val, context_used = super().parse(val=val, ctx=ctx)
        if val is None:
            return val, context_used
        if not isinstance(val, Decimal):
            val = Decimal(val)
        if plus_modifier:
            val += plus_modifier
        elif mult_modifier:
            val *= mult_modifier
        return val, context_used


class IntValueParser(ValueParser):

    PLUS_RE = re.compile(r'^(\$?\w+)([\+\-]\d+)$')
    MULT_RE = re.compile(r'^(\$?\w+)\*(\d+)$')

    @classmethod
    def _parse_modifier(cls, val):
        """
        *<int>
        +<int>
        -<int>
        """
        if not isinstance(val, str):
            return val, None, None

        if val.isdigit():
            return val, None, None

        plus_res = cls.PLUS_RE.search(val)
        if plus_res:
            plus_res = plus_res.groups()
            return plus_res[0], int(plus_res[1]), None

        mult_res = cls.MULT_RE.search(val)
        if mult_res:
            mult_res = mult_res.groups()
            return mult_res[0], None, int(mult_res[1])

        return val, None, None

    @classmethod
    def parse(cls, val, ctx):
        val, plus_modifier, mult_modifier = cls._parse_modifier(val)
        val, context_used = super().parse(val=val, ctx=ctx)
        if val is None:
            return val, context_used
        if not isinstance(val, int):
            val = int(val)
        if plus_modifier:
            val += plus_modifier
        elif mult_modifier:
            val *= mult_modifier
        return val, context_used


class DateTimeValueParser(ValueParser):

    PLUS_RE = re.compile(r'^(\$?[\w\-\:]+)([\+\-]\d+)([dhms])$')

    @classmethod
    def _parse_modifier(cls, val):
        """
        +/-1d/h/m/s
        """
        if not isinstance(val, str):
            return val, None, None

        plus_res = cls.PLUS_RE.search(val)
        if plus_res:
            plus_res = plus_res.groups()
            delta_val = int(plus_res[1])
            is_increase = delta_val >= 0
            delta_val = abs(delta_val)
            if plus_res[2] == 'd':
                delta = datetime.timedelta(days=delta_val)
            elif plus_res[2] == 'h':
                delta = datetime.timedelta(hours=delta_val)
            elif plus_res[2] == 'm':
                delta = datetime.timedelta(minutes=delta_val)
            elif plus_res[2] == 's':
                delta = datetime.timedelta(seconds=delta_val)
            else:
                raise ValueParsingError(f"Invalid time delta: {val}")
            return (
                plus_res[0],
                delta if is_increase else None,
                delta if not is_increase else None
            )

        return val, None, None

    @classmethod
    def parse(cls, val, ctx):
        val, plus_modifier, minus_modifier = cls._parse_modifier(val)
        val, context_used = super().parse(val=val, ctx=ctx)
        if val is None:
            return val, context_used
        if not isinstance(val, datetime.datetime):
            if isinstance(val, str) and val.isdigit():
                val = int(val)
            if isinstance(val, int):
                # utc timestamp
                val = datetime.datetime.utcfromtimestamp(val)
            else:
                val = datetime.datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
        if plus_modifier:
            val += plus_modifier
        elif minus_modifier:
            val -= minus_modifier
        return val, context_used


VALUE_TYPES = {
    'str': ValueParser,
    'bool': BoolValueParser,
    'decimal': DecimalValueParser,
    'int': IntValueParser,
    'datetime': DateTimeValueParser
}


def parse_value(val, val_type, ctx=None):
    """
    val_types:
    - str
    - bool
    - decimal
    - int
    - datetime
    """
    parser = VALUE_TYPES[val_type]
    return parser.parse(val, ctx)
