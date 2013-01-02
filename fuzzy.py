import difflib
from inspect import getmembers, ismethod
import warnings


class FuzzyMatchWarning(UserWarning):
    pass


class FuzzyObject(object):
    '''
    >>> class FuzzyClass(FuzzyObject):
    ...     def method(self):
    ...         return True
    >>> fuzzy = FuzzyClass()
    >>> fuzzy.method()
    True
    >>> fuzzy.mthd()
    True
    >>> fuzzy.error()
    Traceback (most recent call last):
        ...
    AttributeError: 'FuzzyClass' object has no attribute 'error'
    '''

    def __init__(self):
        self.__method_names = set()
        for name, _method in getmembers(self, predicate=ismethod):
            self.__method_names.add(name)

    def __getattr__(self, name):
        names = self.__method_names | set(self.__dict__.keys())
        matches = difflib.get_close_matches(name, names, 1, 0.8)
        if matches:
            warnings.warn('fuzzy matched %r' % matches[0], FuzzyMatchWarning)
            return getattr(self, matches[0])
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, name))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
