from idspy import *


class ds(IDSDataset):
    id = "test"


def test_Entry():
    row = ['1', '100', '', 'form', 'alt_form', '', '', '', '', 'com']
    c = ds()
    e = c.entry_from_row(row)
    assert e.ids_id == '1-100'
    assert e.alt_forms[0] == 'alt_form'
    row[4] = ['alt_form']
    e = c.entry_from_row(row)
    assert e.alt_forms[0] == 'alt_form'


def test_preprocess_form_comment():
    c = ds()
    a, b = c.preprocess_form_comment(' ‰abc (T.) ', 'phonemic', '160', 'com', '1')
    assert a == 'äabc'
    assert b == 'com (T.)'

    a, b = c.preprocess_form_comment('abc?', 'phonemic', '160', 'com', '17-610')
    assert a == 'abc'

    a, b = c.preprocess_form_comment('abc|', 'phonemic', '704', 'com', '1')
    assert a == 'abcǀ'

    a, b = c.preprocess_form_comment('abc T+', 'phonemic', '832', 'com', '1')
    assert a == 'abc'

    a, b = c.preprocess_form_comment('abc +T', 'phonemic', '832', 'com', '1')
    assert a == 'abc'

    a, b = c.preprocess_form_comment('abc R?', 'phonemic', '832', 'com', '1')
    assert a == 'abc'

    a, b = c.preprocess_form_comment('abc.???', 'phonemic', '831', 'com', '1')
    assert a == 'abc.#'

    a, b = c.preprocess_form_comment('PPN abc', 'phonemic', '234', 'com', '1')
    assert a == 'abc'
    assert b == 'PPN; com'

    a, b = c.preprocess_form_comment('PEP abc', 'phonemic', '234', 'com', '1')
    assert a == 'abc'
    assert b == 'PEP; com'

    a, b = c.preprocess_form_comment('abc [def]', 'phonemic', '168', '', '1')
    assert a == 'abc'
    assert b == '[def]'
