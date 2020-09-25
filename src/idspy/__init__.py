import attr
import pylexibank
from clldutils.misc import nfilter
from itertools import chain

__all__ = ['IDSDataset', 'IDSEntry', 'IDSLanguage', 'IDSLexeme']


@attr.s
class IDSLexeme(pylexibank.Lexeme):
    Transcriptions = attr.ib(default=None)
    AlternativeValues = attr.ib(default=None)


@attr.s
class IDSLanguage(pylexibank.Language):
    Authors = attr.ib(default=None)
    DataEntry = attr.ib(default=None)
    Consultants = attr.ib(default=None)
    Representations = attr.ib(default=None)
    alt_names = attr.ib(default=None)
    date = attr.ib(default=None)


class IDSEntry:
    def __init__(self, ids_id, form, alt_forms, comment):
        # alt_forms can be None, a string or a list - ensure
        # that self.alt_forms returns either None or a list
        if alt_forms and isinstance(alt_forms, str):
            self.alt_forms = [alt_forms]
        else:
            self.alt_forms = alt_forms
        self.ids_id = ids_id
        self.form = form
        self.comment = comment


class IDSDataset(pylexibank.Dataset):
    lexeme_class = IDSLexeme
    language_class = IDSLanguage
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")"},
        separators=";",
        missing_data=('?', '-'),
        strip_inside_brackets=False
    )

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

    def get_personnel(self, args):
        personnel = {'author': [], 'data entry': [], 'consultant': []}
        try:
            for d in chain.from_iterable(
                    chain(pylexibank.get_creators_and_contributors(self.dir / "CONTRIBUTORS.md"))):
                if 'name' in d and d['name']:
                    for desc in nfilter([r.strip().lower()
                                        for r in d.get('description', '').split(',')]):
                        if desc in personnel and d['name'] not in personnel[desc]:
                            personnel[desc].append(d['name'])
                else:
                    args.log.warn("No 'name' found in file 'CONTRIBUTORS.md'")
        except FileNotFoundError:
            args.log.warn("File 'CONTRIBUTORS.md' not found")
        return personnel

    def apply_cldf_defaults(self, args):
        """
        Sorts the added parameters according to IDS IDs sort order and
        sets the CLDF separator for appropriate fields of
        LanguageTable and FormTable. It should be called at the end of
        method 'cmd_makecldf(self, args)'
        """

        # set default separators
        for c in ['Authors', 'DataEntry', 'Consultants', 'Representations', 'alt_names']:
            args.writer.cldf['LanguageTable', c].separator = ";"
        for c in ['Transcriptions', 'AlternativeValues']:
            args.writer.cldf['FormTable', c].separator = ";"

        # apply default IDS sort order to parameters
        def _x(s):
            i = s.split('-')
            return (int(i[0]), int(i[1]))
        args.writer.objects['ParameterTable'] = sorted(
            args.writer.objects['ParameterTable'],
            key=lambda i: _x(i['ID'])
        )
