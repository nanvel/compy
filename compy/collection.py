from .context import Context
from .group import Group


class Collection:

    def __init__(self, conf):
        self.context = Context(conf=conf['context'])
        self.groups = []
        for g in conf['groups']:
            self.groups.append(Group(name=g['name'], conf=g['conf']))
            self.context.add_group_conf(
                name=g['name'],
                lock_on_true=g.get('lock_on_true', False),
                lock_on_false=g.get('lock_on_false', False)
            )

    def evaluate(self, updates):
        for key, val in updates.items():
            self.context.update(key, val)
        outcomes = {}
        for group in self.groups:
            outcome = group.evaluate(ctx=self.context)
            self.context.update(f"group_{group.name}", outcome and outcome.is_positive)
            outcomes[group.name] = outcome
        return outcomes

    @property
    def context_watching(self):
        watching = set()
        for group in self.groups:
            for k in group.context_watching:
                watching.add(k)
        return watching

    def dump(self):
        pass

    @classmethod
    def load(cls):
        # adds initials to context
        return cls(conf={})
