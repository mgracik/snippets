class Bunch(dict):
    '''
    >>> arrows = Bunch(left='A', right='D')
    >>> 'left' in arrows and 'right' in arrows
    True
    >>> arrows.left, arrows.right
    ('A', 'D')
    >>> print sorted(arrows.items())
    [('left', 'A'), ('right', 'D')]
    >>> 'up' in arrows
    False
    >>> arrows.up = 'W'
    >>> 'up' in arrows
    True
    >>> print sorted(arrows.items())
    [('left', 'A'), ('right', 'D'), ('up', 'W')]
    >>> arrows.down
    Traceback (most recent call last):
        ...
    AttributeError: 'Bunch' object has no attribute 'down'
    >>> arrows['down']
    Traceback (most recent call last):
        ...
    KeyError: 'down'
    >>> arrows['down'] = 'S'
    >>> for key in sorted(arrows):
    ...     key, arrows[key]
    ('down', 'S')
    ('left', 'A')
    ('right', 'D')
    ('up', 'W')
    >>> del arrows.up
    >>> 'up' in arrows
    False
    >>> del arrows['down']
    >>> 'down' in arrows
    False
    >>> print sorted(arrows.items())
    [('left', 'A'), ('right', 'D')]
    '''

    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__ = self

    def copy(self):
        new_dict = super(Bunch, self).copy()
        return Bunch(new_dict)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
