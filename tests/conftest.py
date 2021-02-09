from pathlib import Path
import pytest

from clldutils.path import copytree


@pytest.fixture
def tmppath(tmpdir):
    return Path(str(tmpdir))


@pytest.fixture
def test_dataset(tmppath):
    copytree(Path(__file__).parent / 'repos', tmppath / 'repos')
    return tmppath / 'repos' / 'datasets' / 'test_dataset' / 'td.py'
