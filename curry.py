'''
>>> @curry
... def f(a, b, c):
...     return a + b + c
>>> f(1, 2, 3)
6
>>> f(1, 2)(3)
6
>>> f(1)(2)(3)
6
'''

import functools


def curry(f, argc=None):
    if argc is None:
        argc = f.func_code.co_argcount

    @functools.wraps(f)
    def wrapper(*args):
        if len(args) < argc:
            def q(*next_args):
                return functools.partial(f, *args)(*next_args)
            return curry(q, argc - len(args))
        else:
            return f(*args)

    return wrapper


if __name__ == '__main__':
    import doctest
    doctest.testmod()
