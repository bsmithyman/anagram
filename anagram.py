"""anagram.py: the wrong way to solve a problem"""

import collections
import imp
import os
import sys


class Anagram(object):
    """Implements parsing of anagrams"""

    def __init__(self, word):
        self.word = word

    @property
    def baseform(self):
        """The word's base form"""
        return ''.join(sorted(self.word.lower()))

    def __hash__(self):
        """Implement hash collisions for anagrams"""
        return hash(self.baseform)

    def __str__(self):
        """Return the string representation"""
        return '{name}(\'{word}\') --> \'{baseform}\''.format(
            name=self.__class__.__name__,
            word=self.word,
            baseform=self.baseform,
            )

    def __repr__(self):
        """Return an evaluable representation"""
        return '{name}("""{word}""")'.format(
            name=self.__class__.__name__,
            word=self.word,
            )


class Originals(set):
    """Tracker to index originals"""

    def __call__(self, word):
        """Track and pass original word"""
        self.add(word)
        return word.baseform


class Tracker(collections.Counter):
    """Tracker to collect anagrams"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.originals = {}

    def __call__(self, words):
        """Intake words"""
        self.update((self.originals.setdefault(pa.baseform, Originals())(pa) \
            for pa in (Anagram(word) for word in words)))

    def __add__(self, other):
        """Implement 'self + other'"""
        result = super().__add__(other)
        result.originals = {key: self.originals.get(key, set()) + other.originals.get(key, set())
                            for key in set(list(self.originals.keys()) + list(other.originals.keys()))}
        return result

    def __str__(self):
        """Return a string representation"""
        mc = self.most_common()
        return '\n'.join(('{} [{}]:\n\t'.format(baseform, count) + \
            ', '.join((pa.word for pa in self.originals[baseform])) \
            for baseform, count in self.most_common()))


class AnagramImporter(object):
    """Implements import mechanics for text files full of potential anagrams"""

    def __init__(self, extension='txt'):
        self.extension = extension

    def find_module(self, fullname, path=None):
        """Locate a matching module"""
        for dirname in sys.path:
            filename = os.path.join(dirname, '.'.join((fullname, self.extension)))
            if os.path.isfile(filename):
                return AnagramLoader(filename, self.extension)


class AnagramLoader(object):
    """Loads a text file of anagrams into a Python object"""

    def __init__(self, filename, extension):
        self.filename = filename
        self.extension = extension

    def load_module(self, fullname):
        """Create a new modules based on the contents of filename"""
        module = sys.modules.setdefault(fullname, imp.new_module(fullname))
        module.__file__ = self.filename
        module.__loader__ = self
        try:
            with open(self.filename) as fp:
                lines = (line.strip() for line in fp.readlines())
        except UnicodeDecodeError:
            with open(self.filename, encoding='latin-1') as fp:
                lines = (line.strip() for line in fp.readlines())
        obj = Tracker()
        obj(lines)
        setattr(module, self.extension, obj)
        return module


sys.meta_path.append(AnagramImporter())
