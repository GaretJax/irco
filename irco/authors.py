import re
from collections import Counter


class NamePart(object):
    def __init__(self, name):
        self.name = name

    def is_abbreviated(self):
        return self.name.endswith('.')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return 'NamePart({!r})'.format(self.name.encode('utf-8'))

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented

        if self.isabbrof(other) or other.isabbrof(self):
            return True

        return False

    def isabbrof(self, other):
        pattern = re.escape(self.name).replace('\.', '.+')
        return re.match(pattern, other.name, re.I) is not None


class Author(unicode):
    def __init__(self, name):
        match = re.match(r'^([^\(]+)(?:\(([^@]+@[^ ]+)\))?$', name)
        self.name, self.email = match.groups()
        self.chunks = self.split_name(self.name)

    def split_name(self, name):
        chunks = []
        for c in name.split(u', '):
            chunks += self.split_chunk(c)
        chunks = sorted(chunks, key=lambda p: p.name)
        return tuple(chunks)

    def split_chunk(self, chunk):
        parts = [c.strip() for c in re.split(r'([. ]{1,2}(?!-))', chunk)]

        i = 0

        while i < len(parts):
            if not parts[i]:
                del parts[i]
            elif parts[i] == '.':
                parts[i-1] += parts[i]
                del parts[i]
            else:
                i += 1

        parts = [NamePart(p) for p in parts]
        parts = sorted(parts, key=lambda p: p.name)
        #print parts
        return tuple(parts)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return 'Author({})'.format(', '.join([repr(c) for c in self.chunks]))

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        if not isinstance(other, Author):
            return False

        if len(self.chunks) != len(other.chunks):
            return False

        self_abbr = Counter([c for c in self.chunks if c.is_abbreviated()])
        self_not_abbr = Counter(self.chunks) - self_abbr

        other = Counter(other.chunks)

        r1 = self._find_and_remove(self_not_abbr, other)
        r2 = self._find_and_remove(self_abbr, other)

        return r1 and r2

    def __hash__(self):
        initials = ''.join(n.name[0] for n in self.chunks).lower()
        return hash(initials)

    def _find_and_remove(self, set1, set2):
        while set1:
            n1, c = set1.popitem()
            if c > 1:
                set1[n1] = c - 1
            for n2 in set2:
                if n1.is_abbreviated() ^ n2.is_abbreviated():
                    continue
                if n1 == n2:
                    set2.subtract([n2])
                    if not set2[n2]:
                        del set2[n2]
                    break
            else:
                for n2 in set2:
                    if n1 == n2:
                        set2.subtract([n2])
                        if not set2[n2]:
                            del set2[n2]
                        break
                else:
                    return False
        return True
