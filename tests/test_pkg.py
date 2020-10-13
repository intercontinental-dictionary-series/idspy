import pathlib

import pytest

from idspy import *


@pytest.fixture(scope='session')
def ds():
    class _ds(IDSDataset):
        id = "test"
        dir = pathlib.Path(__file__).parent / 'ds'
    return _ds()


def test_read_csv(ds):
    assert len(list(ds.read_csv('data.csv'))) == 1


def test_read_get_personnel(ds, mocker):
    assert 'author' in ds.get_personnel(mocker.Mock())


def test_Entry(ds):
    row = ['1', '100', '', 'form', 'alt_form', '', '', '', '', 'com']
    c = ds
    e = c.entry_from_row(row)
    assert e.ids_id == '1-100'
    assert e.alt_forms[0] == 'alt_form'
    row[4] = ['alt_form']
    e = c.entry_from_row(row)
    assert e.alt_forms[0] == 'alt_form'


@pytest.mark.parametrize(
    'f, desc, lid, com, pid,aex,bex',
    [
        (' ‰abc (T.) ', 'phonemic', '160', 'com', '1', 'äabc', 'com (T.)'),
        ('abc?', 'phonemic', '160', 'com', '17-610', 'abc', None),
        ('abc|', 'phonemic', '704', 'com', '1', 'abcǀ', None),
        ('abc T+', 'phonemic', '832', 'com', '1', 'abc', None),
        ('abc +T', 'phonemic', '832', 'com', '1', 'abc', None),
        ('abc R?', 'phonemic', '832', 'com', '1', 'abc', None),
        ('abc.???', 'phonemic', '831', 'com', '1', 'abc.#', None),
        ('PPN abc', 'phonemic', '234', 'com', '1', 'abc', 'PPN; com'),
        ('PEP abc', 'phonemic', '234', 'com', '1', 'abc', 'PEP; com'),
        ('abc [def]', 'phonemic', '168', '', '1', 'abc', '[def]'),
    ]
)
def test_preprocess_form_comment(ds, f, desc, lid, com, pid, aex, bex):
    a, b = ds.preprocess_form_comment(f, desc, lid, com, pid)
    assert a == aex
    if bex is not None:
        assert b == bex
