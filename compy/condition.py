from .outcome import Outcome
from .value import parse_value


COMPARATORS = {
    'eq': lambda a, b: a == b,  # default
    'neq': lambda a, b: a != b,
    'gt': lambda a, b: a > b,
    'gte': lambda a, b: a >= b,
    'lt': lambda a, b: a < b,
    'lte': lambda a, b: a <= b
}


def evaluate_condition(key, value, ctx):
    comparator_slug = key.split('_')
    if not comparator_slug:
        comparator_slug = ['eq']
    comparator_slug = comparator_slug[-1]
    if comparator_slug in COMPARATORS:
        key = key[:-len(comparator_slug)-1]
        comparator = COMPARATORS[comparator_slug]
    else:
        comparator_slug = 'eq'
        comparator = COMPARATORS[comparator_slug]

    is_ts = False
    if key.endswith(':ts'):
        is_ts = True
        key = key[:-3]

    context_variable = ctx.get(key)

    val, ctx_used = parse_value(
        val=value,
        val_type='datetime' if is_ts else context_variable.type,
        ctx=ctx
    )

    if ctx_used:
        ctx_keys = (key, ctx_used)
    else:
        ctx_keys = (key,)

    if context_variable.value is None or val is None:
        return None, ctx_keys

    is_positive = comparator(
        context_variable.ts if is_ts else context_variable.value,
        val
    )

    is_hard = False
    # if hardcoded value at the right side -> locked
    # for ts - can only increase, locked if value locked
    a_locked = context_variable.is_locked
    if a_locked:
        a_can_increase = False
        a_can_decrease = False
    else:
        a_can_increase = True if is_ts else context_variable.can_increase
        a_can_decrease = False if is_ts else context_variable.can_decrease
    b_locked = True
    b_can_increase = False
    b_can_decrease = False
    if ctx_used:
        b_variable = ctx.get(ctx_used)
        b_locked = b_variable.is_locked
        b_is_ts = (ctx_used + ':ts') in value
        if b_locked:
            b_can_increase = False
            b_can_decrease = False
        else:
            b_can_increase = True if b_is_ts else b_variable.can_increase
            b_can_decrease = False if b_is_ts else b_variable.can_decrease
    # if two variables is locked
    # if a > b but a can not decrease and b can not increase, and not None
    # if a < b but a can not increase and b can not decrease, and not None
    a_value = context_variable.ts if is_ts else context_variable.value
    if a_locked and b_locked:
        is_hard = True
    elif a_value is not None and val is not None:
        if a_value >= val:
            if not a_can_decrease and not b_can_increase:
                is_hard = True
            elif a_locked and not b_can_increase:
                is_hard = True
            elif b_locked and not a_can_decrease:
                is_hard = True
        if a_value < val:
            if not a_can_increase and not b_can_decrease:
                is_hard = True
            elif a_locked and not b_can_decrease:
                is_hard = True
            elif b_locked and not a_can_increase:
                is_hard = True

    return Outcome(is_positive=is_positive, is_hard=is_hard), ctx_keys
