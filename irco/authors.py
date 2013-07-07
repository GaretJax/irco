import re


class NamePart(object):
    def __init__(self, name):
        self.name = name

    def is_abbreviated(self):
        return self.name.endswith('.')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return 'NamePart({!r})'.format(self.name)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented

        n1, n2 = self.name, other.name

        if n1 == n2:
            return True

        if n1.endswith('.') and n2.startswith(n1[:-1]):
            return True

        if n2.endswith('.') and n1.startswith(n2[:-1]):
            return True

        return False


class Author(str):
    def __init__(self, name):
        match = re.match('^([^\(]+)(?:\(([^@]+@[^ ]+)\))?$', name)
        self.name, self.email = match.groups()
        self.chunks = self.split_name(self.name)

    def split_name(self, name):
        chunks = []
        for c in name.split(', '):
            chunks += self.split_chunk(c)
        chunks = sorted(chunks, key=lambda p: p.name)
        return tuple(chunks)

    def split_chunk(self, chunk):
        parts = [c.strip() for c in re.split(r'([. ]{1,2})', chunk)]

        if parts[-1] == '':
            del parts[-1]
        for i in range(len(parts) - 1, 0, -2):
            parts[i-1] += parts[i]
            del parts[i]

        parts = [NamePart(p) for p in parts]
        parts = sorted(parts, key=lambda p: p.name)
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

        self_abbr = set([c for c in self.chunks if c.is_abbreviated()])
        self_not_abbr = set(self.chunks) - self_abbr

        other = set(other.chunks)

        return (self._find_and_remove(self_not_abbr, other) and
                self._find_and_remove(self_abbr, other))

    def __hash__(self):
        initials = ''.join(n.name[0] for n in self.chunks).lower()
        return hash(initials)

    def _find_and_remove(self, set1, set2):
        while set1:
            n1 = set1.pop()
            if n1 in set2:
                set2.remove(n1)
                continue
            else:
                for n2 in set2:
                    if n1 == n2:
                        set2.remove(n2)
                        break
                else:
                    return False
                continue
        return True
