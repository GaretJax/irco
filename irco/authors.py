import re
import logging
from collections import Counter


log = logging.get_logger()


class NamePart(object):
    def __init__(self, name):
        self.name = name
        self._preprocess_abbr()

    def _preprocess_abbr(self):
        if self.name.endswith('.'):
            self.is_abbreviated = True
        elif self.name.isupper():
            self.is_abbreviated = True
            self.name = ''.join((c + '.' for c in self.name))
        else:
            self.is_abbreviated = False

    def __len__(self):
        if self.is_abbreviated:
            return sum((c.isupper() for c in self.name))
        else:
            return len(self.name)

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

    def __gt__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented
        return self.name > other.name

    def __lt__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented
        return self.name < other.name

    def __ge__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented
        return self.name >= other.name

    def __le__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented
        return self.name <= other.name

    def isabbrof(self, other):
        pattern = re.escape(self.name).replace('\.', '.+')
        return re.match(pattern, other.name, re.I) is not None


class Author(unicode):
    def __init__(self, name):
        match = re.match(r'^([^\(]+)(?:\(([^@]+@[^ ]+)\))?$', name)
        if not match:
            match = re.match(r'^([^\(]+)\(', name)
            self.name = match.group(0)
            self.email = None
        else:
            self.name, self.email = match.groups()
        self.chunks = self.split_name(self.name)

    @classmethod
    def from_chunks(cls, name, email, chunks):
        self = cls(name)
        self.name = name
        self.email = email
        self.chunks = chunks
        return self

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

        self_abbr = Counter([c for c in self.chunks if c.is_abbreviated])
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
                if n1.is_abbreviated ^ n2.is_abbreviated:
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

    def find_best_match(self, authors):
        authors = set(authors)

        for a in authors:
            if a == self:
                return a

        candidates = [(a, self.match_score(a) - 10 * self.distance(a))
                      for a in authors]
        match = max(candidates, key=lambda a: a[1])[0]
        log.warning('Fuzzy match search for "{}" matched "{}"'.format(
            self.name, match.name))
        return match

    def match_score(self, other):
        score = 0

        abbr = Counter([c for c in self.chunks if c.is_abbreviated])
        full = Counter(self.chunks) - abbr

        other_abbr = Counter([c for c in other.chunks if c.is_abbreviated])
        other_full = Counter(other.chunks) - other_abbr

        def substract(d1, d2):
            common_sum = 0
            for k1, count1 in d1.items():
                for k2, count2 in d2.items():
                    if k1 == k2:
                        in_common = min(count1, count2)
                        common_sum += in_common
                        count1 -= in_common
                        d2[k2] -= in_common
                        if not count1:
                            break
                d1[k1] = count1
            return common_sum

        score += 10 * substract(full, other_full)
        score += 10 * substract(abbr, other_abbr)
        score += 5 * substract(full, other_abbr)
        score += 5 * substract(abbr, other_full)

        for d in (full, abbr, other_full, other_abbr):
            for k in d.values():
                assert k >= 0
                score -= k * 5

        return score

    def distance(self, other):
        p1 = ' '.join([c.name for c in sorted(self.chunks)])
        p2 = ' '.join([c.name for c in sorted(other.chunks)])
        l = len(self.name) * len(other.name)
        return float(levenshtein(p1, p2) ** 2) / l


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
