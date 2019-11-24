import datetime


class ContextVariable:

    def __init__(self, conf):
        self.type = conf['type']
        self.can_increase = conf.get('can_increase', True)
        self.can_decrease = conf.get('can_decrease', True)
        self.lock_values = set(conf.get('lock_values') or [])
        self.value = None
        self.ts = None
        value = conf.get('initial', None)
        if value:
            self.update(value)

    def update(self, val):
        if self.is_locked:
            return
        if self.value is not None:
            if not self.can_increase and val > self.value:
                return
            if not self.can_decrease and val < self.value:
                return
        if self.value != val:
            self.ts = datetime.datetime.utcnow()
            self.value = val

    @property
    def is_locked(self):
        return self.lock_values and self.value in self.lock_values


class Context:
    """
    Setup:
    {
        '<varname>': {
            'type': '<type>',
            'can_increase': True,
            'can_decrease': True,
            'lock_values': [],  # become hard when set one of these
        }
    }
    """

    def __init__(self, conf):
        self.variables = {}
        for key, val in conf.items():
            self.variables[key] = ContextVariable(conf=val)

    def get(self, var_key):
        return self.variables[var_key]

    def update(self, var_key, val):
        self.variables[var_key].update(val)

    def add_group_conf(self, name, lock_on_true=False, lock_on_false=False):
        conf = {
            'type': 'bool'
        }
        if lock_on_true:
            conf['lock_values'] = [True]
        elif lock_on_false:
            conf['lock_values'] = [False]
        self.variables[f"group_{name}"] = ContextVariable(conf=conf)
