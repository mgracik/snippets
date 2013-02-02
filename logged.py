from abc import ABCMeta
from functools import wraps
import inspect
import logging
logger = logging.getLogger(__name__)


def formatargs(args, kwargs):
    arglist = [str(arg) for arg in args]
    for key, val in sorted(kwargs.items()):
        arglist.append('%s=%s' % (key, val))
    return ', '.join(arglist)


def cache(func):
    _cache = {}
    def wrapper(*args, **kwargs):
        key = args + tuple(sorted(kwargs.items()))
        if key not in _cache:
            _cache[key] = func(*args, **kwargs)
        return _cache[key]
    return wrapper


@cache
def inspect_obj(obj):
    result = []
    fname = inspect.getfile(obj)
    try:
        source, lineno = inspect.getsourcelines(obj)
    except IOError as exc:
        result.append(str(exc))
    else:
        source = enumerate(source, lineno)
        for lineno, line in source:
            result.append('%s:%s:%s' % (fname, lineno, line.rstrip()))
    return result


def log_pre_cb(func, cls, args, kwargs):
    display_name = getattr(func, 'display_name', None) or func.__name__
    strargs = formatargs(args, kwargs)
    logger.debug('%s.%s(%s)', cls or '<None>', display_name, strargs)
    for line in inspect_obj(func):
        logger.debug(line)


def log_post_cb(func, cls, args, kwargs, returnval):
    logger.debug('==> %s', returnval)


def logfunction(func, cls=None, pre_cb=log_pre_cb, post_cb=log_post_cb):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pre_cb(func, cls, args, kwargs)
        returnval = func(*args, **kwargs)
        post_cb(func, cls, args, kwargs, returnval)
        return returnval
    return wrapper


class Logged(object):

    __metaclass__ = ABCMeta

    def _log_pre_cb(self, func, cls, args, kwargs):
        log_pre_cb(func, cls, args, kwargs)

    def _log_post_cb(self, func, cls, args, kwargs, returnval):
        log_post_cb(func, cls, args, kwargs, returnval)

    def __getattribute__(self, name):
        attr = super(Logged, self).__getattribute__(name)
        if callable(attr) and name not in ('_log_pre_cb', '_log_post_cb'):
            pre_cb = super(Logged, self).__getattribute__('_log_pre_cb')
            post_cb = super(Logged, self).__getattribute__('_log_post_cb')
            attr = logfunction(attr, self, pre_cb, post_cb)
        return attr
