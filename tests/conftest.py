from pathlib import Path
import shutil

import pytest


@pytest.fixture
def test_dataset(tmp_path):
    shutil.copytree(Path(__file__).parent / 'repos', tmp_path / 'repos')
    return tmp_path / 'repos' / 'datasets' / 'test_dataset' / 'td.py'

