import shlex
import pathlib
import openpyxl

from cldfbench.__main__ import main


def _main(cmd, **kw):
    main(['--no-config'] + shlex.split(cmd), **kw)


def test_create_language_sheet(test_dataset):
    _main('idspy.create_language_sheet --lang-id 26 --add-representations " a , b" {}'.format(
        test_dataset)
    )

    wb_path = test_dataset.parent / 'etc' / 'Avar_Batlukh_dialect-26.xlsx'
    assert wb_path.exists()

    wa = openpyxl.load_workbook(wb_path).active
    assert wa['D2'].value == 'дуниял'
    assert wa['F1'].value == 'a'
    assert wa['G1'].value == 'b'
    assert wa['H1'].value == 'Comment'
    assert wa['A5'].value is None
