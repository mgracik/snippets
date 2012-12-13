import collections
import itertools


def flatten(seq):
    '''
    >>> list(flatten([[[0], 1, 2], [3, 4], [5, [6, 7, [8]]], 9]))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(flatten(['aa', ['bb', 'cc'], [['dd', 'ee'], 'ff']]))
    ['aa', 'bb', 'cc', 'dd', 'ee', 'ff']
    '''

    for item in seq:
        if isinstance(item, collections.Iterable) and not isinstance(item, str):
            for subitem in flatten(item):
                yield subitem
        else:
            yield item


def partition(seq, func=bool, func_range=(True, False)):
    '''
    >>> map(list, partition(range(10), func=lambda x: x % 2 == 0))
    [[0, 2, 4, 6, 8], [1, 3, 5, 7, 9]]
    >>> map(list, partition(range(10), func=lambda x: x % 3, func_range=(0, 1, 2)))
    [[0, 3, 6, 9], [1, 4, 7], [2, 5, 8]]
    '''

    buffers = {x: collections.deque() for x in func_range}

    def values(x, seq=iter(seq)):
        while True:
            while not buffers[x]:
                item = seq.next()
                buffers[func(item)].append(item)
            yield buffers[x].popleft()

    return tuple(values(x) for x in func_range)


def unique(seq, key=None):
    '''
    >>> list(unique('ABBA'))
    ['A', 'B']
    >>> list(unique('ABBAabba'))
    ['A', 'B', 'a', 'b']
    >>> list(unique('ABBAabba', key=str.lower))
    ['A', 'B']
    '''

    seen = set()
    if key:
        for elem in seq:
            if key(elem) not in seen:
                seen.add(key(elem))
                yield elem
    else:
        for elem in itertools.ifilterfalse(seen.__contains__, seq):
            seen.add(elem)
            yield elem


def groupjoin(s, sep, groupby):
    return sep.join([''.join(x[::-1]) for x in itertools.izip_longest(*[iter(s[::-1])] * groupby, fillvalue='')][::-1])


def mac(s):
    '''
    >>> mac('aabbccddeeff')
    'aa:bb:cc:dd:ee:ff'
    '''

    return groupjoin(s, sep=':', groupby=2)


def thousands(n, sep=','):
    '''
    >>> map(thousands, [100, -100, 1000, -1000, 1000000, -1000000])
    ['100', '-100', '1,000', '-1,000', '1,000,000', '-1,000,000']
    >>> thousands(1000000, sep='.')
    '1.000.000'
    '''

    prefix, n = ('-', -n) if n < 0 else ('', n)
    return prefix + groupjoin(str(n), sep, groupby=3)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
