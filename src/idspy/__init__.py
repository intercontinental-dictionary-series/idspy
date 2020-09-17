import pathlib

import attr
import pylexibank

__all__ = ['IDSDataset', 'IDSEntry', 'IDSLanguage', 'IDSLexeme']


@attr.s
class IDSLexeme(pylexibank.Lexeme):
    Transcription = attr.ib(default=None)
    AlternativeValue = attr.ib(default=None)
    AlternativeTranscription = attr.ib(default=None)


@attr.s
class IDSLanguage(pylexibank.Language):
    Contributors = attr.ib(default=None)
    default_representation = attr.ib(default=None)
    alt_representation = attr.ib(default=None)
    alt_names = attr.ib(default=None)
    date = attr.ib(default=None)


class IDSEntry:
    def __init__(self, ids_id, form, alt_form, comment):
        self.ids_id = ids_id
        self.form = form
        self.alt_form = alt_form
        self.comment = comment


class IDSDataset(pylexibank.Dataset):
    dir = pathlib.Path(__file__).parent

    lexeme_class = IDSLexeme
    language_class = IDSLanguage

    def entry_from_row(self, row):
        """
        Override to customize how the IDS dictionary template is interpreted.

        :param row:
        :return: An `IDSEntry` instance.
        """
        return IDSEntry("%s-%s" % (row[0], row[1]), row[3], row[4], row[9])

    def read_csv(self, fname):
        for i, row in enumerate(self.raw_dir.read_csv(fname)):
            row = [c.strip() for c in row[0:10]]
            if i > 0:
                row[0:2] = [int(float(c)) for c in row[0:2]]
                yield self.entry_from_row(row)
