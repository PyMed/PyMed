import os.path as op
from nose.tools import assert_raises, assert_true
from ..pymed import PubmedRecord, Records, read_records,\
                    write_records, resolve_doi, query_records
from ..utils import _TempDir

tempdir = _TempDir()
base_dir = op.join(op.dirname(__file__))
recs = read_records(op.join(base_dir, 'test_recs.json'))


def test_read_write_records():
    """ Test reading and writing records"""
    temp_file = op.join(tempdir, 'foo.json')
    recs.save(temp_file)
    recs2 = read_records(temp_file)
    assert_true(recs == recs2)


def test_resolve_doi():
    pass


def test_query_records():
    pass


def test_index_filter_records():
    pass


def test_records_copy():
    """ Test copying records """
    recs1 = recs.copy()
    recs1.pop(0)
    assert_true(len(recs1) != len(recs))


def test_records_selection():
    """ Test indexing and seleciton operation """
    # test slicing
    recs1 = Records(recs[:2])

    # test repr
    for r_ in [recs, recs1]:
        st = '%s' % r_
        assert_true(int(st.split(' | ')[1][0]) == len(r_))

    assert_true(recs1 == recs[:2])

    # test drop
    recs_ = recs.copy()
    rec = recs_[0]
    recs_.exclude_.append(0)
    recs_.drop()
    assert_true(not recs_.exclude_)
    assert_true(rec not in recs_)

    # test insert
    recs_.insert(0, rec)
    assert_true(recs_ == recs)
    recs_.exclude_.append(1)
    assert_raises(RuntimeError, recs_.insert, 0, rec)
    # test aadd
    recs1, recs2 = recs[:1], recs[1:]
    assert_true(recs == recs1 + recs2)
    # test iadd
    recs1 += recs2
    assert_true(recs == recs1)
    for func in [recs1.__iadd__, recs1.__iadd__]:
        assert_raises(TypeError, func, recs2.tolist())
    recs1.append(recs2[0])
    assert_true(recs2[0] in recs1)
    assert_raises(TypeError, recs1.append, 'foo')

    # test filtering
    recs2 = Records(r for r in recs if r.year > 2012)
    assert_true(2012 not in [r.year for r in recs2])

    # test match
    mystring = ' spam eggs spam eggs'
    recs[0]['AB'] += mystring
    found = recs.find(mystring)
    assert_true(found == recs[:1])
    assert_true(found[0].match(mystring))


def test_pubmed_record():
    pass
