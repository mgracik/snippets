from functools import wraps
import inspect


def typechecked(f, *args, **kwargs):
    argspec = inspect.getfullargspec(f)

    def check(arg, val):
        annotation = argspec.annotations.get(arg)
        if annotation and not isinstance(val, annotation):
            raise TypeError('%s has to be %s' % (arg, annotation))

    @wraps(f)
    def wrapper(*args, **kwargs):
        for index, val in enumerate(args):
            arg = argspec.args[index]
            check(arg, val)
        for arg, val in sorted(kwargs.items()):
            check(arg, val)
        return f(*args, **kwargs)
    return wrapper


@typechecked
def add(a: int, b: int):
    return a + b
