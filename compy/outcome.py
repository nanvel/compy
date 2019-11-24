class Outcome:

    def __init__(self, is_positive: bool, is_hard: bool):
        self.is_positive = is_positive
        self.is_hard = is_hard

    def __eq__(self, other):
        return other.is_positive == self.is_positive and other.is_hard == self.is_hard

    def __str__(self):
        return f"{'hard' if self.is_hard else 'soft'} {'positive' if self.is_positive else 'negative'}"


POSITIVE_HARD = Outcome(is_positive=True, is_hard=True)
POSITIVE_SOFT = Outcome(is_positive=True, is_hard=False)
NEGATIVE_HARD = Outcome(is_positive=False, is_hard=True)
NEGATIVE_SOFT = Outcome(is_positive=False, is_hard=False)
