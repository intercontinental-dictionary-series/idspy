import attr
import pylexibank
from clldutils.misc import nfilter
from itertools import chain
import unicodedata
import re

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

    # --- the following code should only be used for the general IDS data repo --- #
    cyrill2phonemic_lgs = list(range(26, 36)) + list(range(37, 43))\
        + list(range(50, 53)) + list(range(54, 76))\
        + [80, 81, 107, 160, 162, 164, 165, 166, 316, 317]\
        + list(range(500, 535))

    def norm(self, f, desc, lid):
        """
        Normalize systematic issues
        """
        f_ = re.sub(r'[’‘′´]', 'ʼ', f.strip())
        for s, r in [
                    ('\u007f', ''),
                    ('\uf11e', '\ufffd'),
                    ('\uf8ff', '\ufffd'),
                    ('\u2028', ' '),
                    (' )', ')')
                ]:
            f_ = f_.replace(s, r)
        if desc and desc.lower() == 'phonemic' and\
                int(lid) in self.cyrill2phonemic_lgs:
            for s, r in [
                        ("'", 'ʼ'),
                        ('ћ', 'ħ'),
                        ('ӡ', 'ʒ'),
                        ('‰', 'ä'),
                        ('ﬁ', 'ˤ'),
                        ('Ɂ', 'ʔ'),
                        ('ӣ', 'ī'),
                        ('ё', 'ö'),
                        ('ť', 'tʼ'),
                        ('t̛', 'tʼ'),
                        ('q̛', 'qʼ'),
                        ('k̛', 'kʼ'),
                        ('Ι', 'ʕ'),
                        ('λ', 'ɬ'),
                        ('č̛', 'čʼ'),
                        ('c̛', 'cʼ')
                    ]:
                f_ = f_.replace(s, r)
            # replace cyrillic letters which should be latin one
            # and decompose them in beforehand
            f_ = unicodedata.normalize('NFD', f_)
            for s, r in [
                        ('е', 'e'),
                        ('а', 'a'),
                        ('о', 'o'),
                        ('х', 'x'),
                        ('у', 'u'),
                        ('с', 'c')
                    ]:
                f_ = f_.replace(s, r)
        return unicodedata.normalize('NFC', f_)

    def preprocess_form_comment(self, f, desc, lid, com, pid):
        """
        Correct/clean systematic issues with comments and normalize forms
        """

        def cc(str, s):
            return '{0}{1}{2}'.format(str if str else '', ' ' if str else '', s)

        f_ = self.norm(f, desc, lid)
        com_ = com.replace('\u2028', ' ')
        com_ = com_.replace('\u00a0', '')
        com_ = com_.replace('\u007f', '')
        com_ = com_.replace('( ', '(')
        com_ = com_.replace(' )', ')')

        # catch final (?)
        if re.search(r' ?\(\?\)$', f_):
            f_ = re.sub(r' ?\(\?\)$', '', f_)
            com_ = cc(com_, '(?)')

        # catch check p.20
        if f_.endswith(' check p.20'):
            f_ = f_.replace(' check p.20', '')
            com_ = cc(com_, 'check p.20')

        # catch (sb.)
        if f_.endswith(' (sb.)'):
            f_ = f_.replace(' (sb.)', '')
            com_ = cc(com_, '(sb.)')

        # catch (f.)
        if f_.endswith(' (f.)'):
            f_ = f_.replace(' (f.)', '')
            com_ = cc(com_, '(f.)')

        # catch (m.)
        if f_.endswith(' (m.)'):
            f_ = f_.replace(' (m.)', '')
            com_ = cc(com_, '(m.)')

        # catch (T(+...))
        m = re.findall(r'( *(\( *T\.?(\+N.?)?\)) *$)', f_)
        if m and len(m[0]) == 3:
            f_ = f_.replace(m[0][0], '')
            com_ = cc(com, m[0][1])

        # catch (N(+...))
        m = re.findall(r'( *(\( *[NK]\.?\+ *T\.?\)) *$)', f_)
        if m and len(m[0]) == 2:
            f_ = f_.replace(m[0][0], '')
            com_ = cc(com_, m[0][1])

        return f_.strip(), com_.strip()
