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

    def get(self, *args, **kwargs):
        return self._config.get(self._section, *args, **kwargs)

    def getint(self, *args, **kwargs):
        return self._config.getint(self._section, *args, **kwargs)

    def getfloat(self, *args, **kwargs):
        return self._config.getfloat(self._section, *args, **kwargs)

    def getboolean(self, *args, **kwargs):
        return self._config.getboolean(self._section, *args, **kwargs)

    @property
    def name(self):
        return self._section


class ConfigParser(configparser.SafeConfigParser):

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
