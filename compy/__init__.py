from decimal import getcontext

from .collection import Collection


getcontext().prec = 20


__all__ = ('Collection',)
