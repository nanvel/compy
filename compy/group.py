from .condition import evaluate_condition
from .outcome import NEGATIVE_HARD, Outcome


class Group:

    def __init__(self, name: str, conf: dict):
        """
        Creates a group of conditions evaluated with AND
        {
            'a': '10',
            'b_gt': 1,
            'c_lte': '$d*1.5'
        }
        """
        self.name = name
        self.outcome = None
        self.conf = conf
        self.hard_outcomes = {}
        self.condition_keys = {}

    @property
    def context_watching(self):
        if self.outcome and self.outcome.is_hard:
            return set()
        if not self.condition_keys:
            raise AssertionError("Evaluation required for context_watching attribute")
        watching = set()
        for key in self.conf:
            if key not in self.hard_outcomes:
                for k in self.condition_keys[key]:
                    watching.add(k)
        return watching

    def evaluate(self, ctx):
        if self.outcome and self.outcome.is_hard:
            return self.outcome

        results = []
        for key, val in self.conf.items():
            if key in self.hard_outcomes:
                results.append(Outcome(is_positive=self.hard_outcomes[key], is_hard=True))
                continue

            out, ctx_keys = evaluate_condition(key, val, ctx=ctx)
            self.condition_keys[key] = ctx_keys

            if out and out == NEGATIVE_HARD:
                self.outcome = Outcome(is_positive=False, is_hard=True)
                return self.outcome
            results.append(out)

        if any([r is None for r in results]):
            self.outcome = None
            return self.outcome

        if all([r.is_positive for r in results]):
            is_hard = all([r.is_hard for r in results])
            self.outcome = Outcome(is_positive=True, is_hard=is_hard)
            return self.outcome

        self.outcome = Outcome(is_positive=False, is_hard=False)
        return self.outcome
