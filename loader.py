from contextlib import contextmanager
import imp
import logging
logger = logging.getLogger(__name__)
import os
import sys


def _iter_modules(pathlist, extensions=None):
    for fullpath in pathlist:
        path, filename = os.path.split(fullpath)
        modname, ext = os.path.splitext(filename)
        if extensions and ext not in extensions:
            logger.debug('Skipping %s: Wrong extension (%s)', fullpath, ext)
            continue
        yield modname, fullpath


def _import_module(modname, path='', prefix=''):

    @contextmanager
    def no_bytecode():
        default = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        yield
        sys.dont_write_bytecode = default

    with no_bytecode():
        try:
            module = imp.load_source('%s%s' % (prefix, modname), path)
        except Exception as exc:
            # TODO
            raise
        else:
            return module


def _iter_subclasses(cls, _seen=None):
    if _seen is None:
        _seen = set()

    try:
        subclasses = cls.__subclasses__()
    except TypeError:
        # Fails only when cls is type.
        subclasses = cls.__subclasses__(cls)

    for subclass in subclasses:
        if subclass not in _seen:
            _seen.add(subclass)
            yield subclass
            for subclass in iter_subclasses(subclass, _seen):
                yield subclass


def load_modules(pathlist, extensions=None, cls=None, prefix=''):
    ''' Import all filenames in pathlist as python modules.

    If a list of file extensions is specified, filenames with different
    extensions will be skipped, otherwise all filenames will be imported.

    Returns an iterator over all available subclasses of cls, after all modules
    have been imported.
    '''

    if cls is None:
        raise TypeError, 'cls must not be None'

    modules = _iter_modules(pathlist, extensions)
    imported = {mod: _import_module(*mod, prefix=prefix) for mod in modules}
    if not imported:
        logger.warning('No modules found')
    return _iter_subclasses(cls)
