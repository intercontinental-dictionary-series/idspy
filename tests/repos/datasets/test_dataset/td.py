import pathlib

from idspy import IDSDataset


class Dataset(IDSDataset):
    dir = pathlib.Path(__file__).parent
    id = "test_ids"
