# -*- coding: utf-8 -*-
import collections
import itertools
import sys


class Namespace(object):
    __slots__ = ['_dict']

    def __init__(self, values=None):
        self._dict = {}
        if values:
            self._dict.update(values)

    def __contains__(self, k):
        return k in self._dict


    def __getitem__(self, k):
        return self._dict[k]

    def __setitem__(self, k, v):
        self._dict[k] = v

    def __getattr__(self, k):
        try:
            return self._dict[k]
        except KeyError:
            try:
                return getattr(self._dict, k)
            except:
                raise
                # print "DEBUG: unknown identifier:", k
                # print "DEBUG: known identifiers:", self._dict.keys ( )
                # return 'Unknown identifier:%s' % k


def quoteattrs(attrs):
    """
    Escape and quote a dict of attribute/value pairs.

    Escape &, <, and > in a string of data, then quote it for use as
    an attribute value.  The " character will be escaped as well.
    Also filter out None values.
    """
    quoted = []
    for a, v in attrs.items():
        if v is None:
            continue
        if not isinstance(v, str):
            v = str(v, 'utf-8')

        v = u'"' + v.replace(u"&", u"&amp;"
                             ).replace(u">", u"&gt;"
                                       ).replace(u"<", u"&lt;"
                                                 ).replace(u'"', u"&quot;") + u'"'
        quoted.append(u' %s=%s' % (a, v))
    return quoted


def escape(s):
    """
    Escape &, <, and > in a string of data.
    """
    return s.replace("&", "&amp;"
                     ).replace(">", "&gt;"
                               ).replace("<", "&lt;")


def caller():
    """
    get the execution frame of the caller
    """
    return sys._getframe(2)


class PrettyPrinter(object):
    """not happy with this - should happen at the flattener level"""

    def __init__(self, indent=2):
        self.indent = indent
        self.current_indent = -indent
        self.output = []

    def start_element(self, name, attrs):
        self.current_indent += self.indent
        padding = ' ' * self.current_indent
        if attrs:
            self.output.append(
                padding +
                "<%s%s>" % (name, ''.join(quoteattrs(attrs)))
            )
        else:
            self.output.append(padding + "<%s>" % name)

    def end_element(self, name):
        padding = ' ' * self.current_indent
        self.output.append(padding + "</%s>" % name)
        self.current_indent -= self.indent

    def char_data(self, data):
        padding = ' ' * (self.current_indent + self.indent)
        self.output.append(padding + data)

    def parse(self, xmldata):
        from xml.parsers.expat import ParserCreate  # @UnresolvedImport

        p = ParserCreate('utf-8')
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        p.Parse(xmldata)
        return '\n'.join(self.output)



def izip_flat_pairs(pairs, fillvalue=None):
    it = iter(pairs)
    return itertools.zip_longest(it, it, fillvalue=fillvalue)


class odict(collections.OrderedDict):
    def __init__(self, *args, **kwds):
        """
        Initialize an ordered dictionary. The signature is almost the same as regular dictionaries,
        but keyword arguments are not recommended because their insertion order is arbitrary.

        And additional:
        * If an even number of args is given, they are used as flat key value pairs.
        * Borrowed adict functionality for names without "__" in front

        """
        if len(args) > 1:
            if len(args) % 2 != 0:
                raise TypeError('expected one or an even number of args, got %d' % len(args))
            args = izip_flat_pairs(args),
        super().__init__(*args, **kwds)

    def update(*args, **kwds):  # @NoSelf
        ''' D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
            If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
            If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
            In either case, this is followed by: for k, v in F.items(): D[k] = v
        '''
        if not args:
            raise TypeError("descriptor 'update' of 'MutableMapping' object "
                            "needs an argument")
        self, *args = args
        if len(args) > 1:
            if len(args) % 2 != 0:
                raise TypeError('expected one or an even number of args, got %d' % len(args))
            args = izip_flat_pairs(args),
        if args:
            other = args[0]
            if isinstance(other, collections.Mapping):
                for key in other:
                    self[key] = other[key]
            elif hasattr(other, "keys"):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwds.items():
            self[key] = value

    def __getattr__(self, name):
        if name.startswith('__'):
            return super(odict, self).__getattr__(self, name)
        try:
            return self[name]
        except KeyError:
            raise self.__attr_error(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(odict, self).__setattr__(name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        if name.startswith('_'):
            super(odict, self).__delattr__(name)

        try:
            del self[name]
        except KeyError:
            raise self.__attr_error(name)

    def __attr_error(self, name):
        return AttributeError("type object '{subclass_name}' has no attribute '{attr_name}'"
                              .format(subclass_name=type(self).__name__, attr_name=name))

    def copy(self):
        return odict(dict.copy(self))
