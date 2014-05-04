import pytest
from collections import namedtuple
from irco.authors import Author, NamePart, levenshtein


AuthorTestSet = namedtuple('AuthorTestSet',
                           ['corresponding', 'expected', 'candidates'])

corresponding_authors = [
    (u'Ei-Shazly, M', 0, (u'EI-Shazly, M.', u'Eissa, B.')),
    (u'Pan, WH', 0, (u'Weihua, Pan',
                     u'Liao, Wanqing',
                     u'Khayhan, Kantarawee',
                     u'Hagen, Ferry',
                     u'Boekhout, Teun',
                     u'Khayhan, Kantarawee',
                     u'Hagen, Ferry',
                     u'Boekhout, Teun',
                     u'Khayhan, Kantarawee',
                     u'Wahyuningsih, Retno',
                     u'Sjam, Ridhawati',
                     u'Wahyuningsih, Retno',
                     u'Chakrabarti, Arunaloke',
                     u'Chowdhary, Anuradha',
                     u'Ikeda, Reiko',
                     u'Taj-Aldeen, Saad J.',
                     u'Khan, Ziauddin',
                     u'Imran, Darma',
                     u'Imran, Darma',
                     u'Sriburee, Pojana',
                     u'Chaicumpar, Kunyaluk',
                     u'Ingviya, Natnicha',
                     u'Mouton, Johan W.',
                     u'Curfs-Breuker, Ilse',
                     u'Meis, Jacques F.',
                     u'Klaassen, Corne H. W.',
                     u'Mouton, Johan W.',
                     u'Meis, Jacques F.')),
    (u'Abu-Shady, ASI', 2, (u'Al-Mudhaf, Humood F.',
                            u'Al-Hayan, Mohammad N.',
                            u'Abu-Shady, Abdel-Sattar I.',
                            u'Selim, Mustafa I.')),
    (u'Al-Tahan, ARM', 0, (u'Al-Tahan, Abdel-Rahman M.',
                           u'Al-Jumah, Mohammed A.',
                           u'Bohlega, Saeed M.',
                           u'Al-Shammari, Suhail N.',
                           u'Al-Sharoqi, Isa A.',
                           u'Dahdaleh, Maurice P.',
                           u'Hosny, Hassan M.',
                           u'Yamout, Bassem I.')),
    (u'Elassar, AZA', 0, (u'Elassar, Abdel-Zaher A.',
                          u'Al-Fulaij, Othman A.',
                          u'El-Sayed, Ahmed E. M.',
                          u'Elassar, Abdel-Zaher A.')),
    (u'Muller, HP', 0, (u'Mueller, Hans-Peter',
                        u'Barrieshi-Nusair, Kefah M.')),
    (u'Chen, HH', 0, (u'Chen, Hsiao-Hwa',
                      u'Xiao, Yang',
                      u'Chen, Hui',
                      u'Du, Xiaojiang',
                      u'Guizani, Mohsen'
                      )),
    (u'Mosaad, MES', 0, (u'Mosaad, M. El-Sayed',
                         u'Al-Hajeri, M.',
                         u'Al-Ajmi, R.',
                         u'Koliub, Abo. M.')),
    (u'Heo, MS', 4, (u'Harikrishnan, Ramasamy',
                     u'Moon, Young-Gun',
                     u'Kim, Man-Chul',
                     u'Kim, Ju-Sang',
                     u'Heo, Moon-Soo',
                     u'Jin, Chang-Nam',
                     u'Balasundaram, Chellam',
                     u'Azad, I. S.')),
    (u'Khedr, MEM', 0, (u'Khedr, M. -E. M.',
                        u'Chamkha, A. J.',
                        u'Bayomi, M.')),
]


@pytest.fixture(params=corresponding_authors)
def corresponding_author(request):
    corresponding, expected, candidates = request.param
    candidates = [Author(c) for c in candidates]
    expected = candidates[expected]
    return AuthorTestSet(Author(corresponding), expected, candidates)


def test_authors(corresponding_author):
    corresponding, expected, candidates = corresponding_author
    match = corresponding.find_best_match(candidates)
    assert match
    assert match == expected


def test_namepart_isabbrof():
    assert NamePart('WH').isabbrof(NamePart('Weihua'))


def test_chunks():
    a1 = Author('Ei-Shazly, M').chunks
    a2 = Author('EI-Shazly, M.').chunks
    assert a1 == a2

    n1 = NamePart('H.H.')
    n2 = NamePart('Hsiao-Hwa')
    n3 = NamePart('Hui')
    assert n1 == n2
    assert n1 != n3
    assert n2 != n3


def _test_match_score():
    corr, expected, cand = corresponding_authors[8]
    corr = Author(corr)
    print
    print corr, corr.chunks
    print
    import difflib
    scored_can = []
    for a in cand:
        p1 = ' '.join([c.name for c in sorted(corr.chunks)])
        p2 = ' '.join([c.name for c in sorted(Author(a).chunks)])
        l = levenshtein(p1, p2)
        l = float(l ** 2) / len(a) / len(corr.name)
        c = corr.match_score(Author(a))
        scored_can.append((
            Author(a),
            c,
            l,
            c - 10 * l,
            corr.distance(Author(a))
        ))

    for a, c, l, c2, d in scored_can:
        print a.chunks, c, l, c2, d

    print
    print 'Score:', max(scored_can, key=lambda c: c[1])
    print 'Leven:', min(scored_can, key=lambda c: c[2])
    print 'Mixed:', max(scored_can, key=lambda c: c[3])
    print 'Implemented:', min(scored_can, key=lambda c: c[4])
    print 'Diff:', difflib.get_close_matches(corr.name, cand, 1)
