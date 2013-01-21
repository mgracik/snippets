import ConfigParser as configparser


class ConfigSection(object):

    def __init__(self, config, section):
        self._config = config
        self._section = section

    def __setitem__(self, option, value):
        self._config.set(self._section, option, value)

    def __getitem__(self, option):
        return self._config.get(self._section, option)

    def __delitem__(self, option):
        return self._config.remove_option(self._section, option)

    def __contains__(self, option):
        return self._config.has_option(self._section, option)

    def items(self):
        return self._config.items(self._section)

    def iteritems(self):
        return iter(self.items())

    def keys(self):
        return self._config.options(self._section)

    def iterkeys(self):
        return iter(self.keys())

    def __iter__(self):
        return self.iterkeys()

    def __str__(self):
        items = ['(%r, %r)' % item for item in self.items()]
        return '%s([%s])' % (self.__class__.__name__, ', '.join(items))

    def _get(self, getter, option, fallback):
        if option not in self:
            return fallback
        else:
            getter = getattr(configparser.ConfigParser, getter)
            return getter(self._config, self._section, option)

    def get(self, option, fallback=None):
        return self._get('get', option, fallback)

    def getint(self, option, fallback=None):
        return self._get('getint', option, fallback)

    def getfloat(self, option, fallback=None):
        return self._get('getfloat', option, fallback)

    def getboolean(self, option, fallback=None):
        return self._get('getboolean', option, fallback)

    @property
    def name(self):
        return self._section


class ConfigParser(configparser.SafeConfigParser):
    '''
    >>> config = ConfigParser(dict_type=SortedDict)
    >>> config['DEFAULT'] = {'ServerAliveInterval': '45',
    ...                      'Compression': 'yes',
    ...                      'CompressionLevel': '9'}
    >>> config['bitbucket.org'] = {}
    >>> config['bitbucket.org']['User'] = 'hg'
    >>> config['topsecret.server.com'] = {}
    >>> topsecret = config['topsecret.server.com']
    >>> topsecret['Port'] = '50022'     # mutates the parser
    >>> topsecret['ForwardX11'] = 'no'  # same here
    >>> config['DEFAULT']['ForwardX11'] = 'yes'
    >>> config.sections()
    ['bitbucket.org', 'topsecret.server.com']
    >>> 'bitbucket.org' in config
    True
    >>> 'bytebong.com' in config
    False
    >>> config['bitbucket.org']['User']
    'hg'
    >>> config['DEFAULT']['Compression']
    'yes'
    >>> topsecret = config['topsecret.server.com']
    >>> topsecret['ForwardX11']
    'no'
    >>> topsecret['Port']
    '50022'
    >>> for key in config['bitbucket.org']: print(key)
    ...
    Compression
    CompressionLevel
    ForwardX11
    ServerAliveInterval
    User
    >>> config['bitbucket.org']['ForwardX11']
    'yes'
    >>> topsecret.getboolean('ForwardX11')
    False
    >>> config['bitbucket.org'].getboolean('ForwardX11')
    True
    >>> config.getboolean('bitbucket.org', 'Compression')
    True
    >>> topsecret.get('Port')
    '50022'
    >>> topsecret.get('CompressionLevel')
    '9'
    >>> topsecret.get('Cipher')
    >>> topsecret.get('Cipher', '3des-cbc')
    '3des-cbc'
    >>> topsecret.get('CompressionLevel', '3')
    '9'
    >>> config.get('bitbucket.org', 'monster',
    ...            fallback='No such things as monsters')
    'No such things as monsters'
    >>> 'BatchMode' in topsecret
    False
    >>> topsecret.getboolean('BatchMode', fallback=True)
    True
    >>> config['DEFAULT']['BatchMode'] = 'no'
    >>> topsecret.getboolean('BatchMode', fallback=True)
    False
    '''

    def __setitem__(self, section, options):
        if not section in self and section != 'DEFAULT':
            self.add_section(section)
        for option, value in options.items():
            self.set(section, option, value)

    def __getitem__(self, section):
        return ConfigSection(self, section)

    def __delitem__(self, section):
        return self.remove_section(section)

    def __contains__(self, section):
        return self.has_section(section)

    def __iter__(self):
        return iter(self.sections())

    def __str__(self):
        sections = []
        for section in self.sections():
            sections.append('(%r, %r)' % (section, ConfigSection(self, section)))
        return '%s([%s])' % (self.__class__.__name__, ', '.join(sections))

    def defaults(self):
        return ConfigSection(self, 'DEFAULT')

    def optionxform(self, option):
        return option

    def get(self, section, option, fallback=None):
        try:
            return configparser.ConfigParser.get(self, section, option)
        except configparser.NoOptionError:
            return fallback


class SortedDict(dict):

    def copy(self):
        return SortedDict(super(SortedDict, self).copy())

    def items(self):
        return sorted(super(SortedDict, self).items())

    def iteritems(self):
        return iter(self.items())

    def keys(self):
        return sorted(super(SortedDict, self).keys())

    def iterkeys(self):
        return iter(self.keys())

    def values(self):
        return sorted(super(SortedDict, self).values())

    def itervalues(self):
        return iter(self.values())

    def __iter__(self):
        return self.iterkeys()

    def __str__(self):
        items = ['(%r, %r)' % item for item in self.items()]
        return '%s([%s])' % (self.__class__.__name__, ', '.join(items))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
