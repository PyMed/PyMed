# Authors: Denis A. Engemann <denis.engemann@gmail.com>
#          Danilo Bzdok <danilobzdok@gmail.com>
#
# License: BSD (3-clause)

import json
import re
import textwrap
from copy import deepcopy
from .constants import PMD

from Bio import Entrez, Medline

try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, HTTPError

DOI_REGEX = '(10\\.\\d{4,6}/[^"\'&<% \t\n\r\x0c\x0b]+)'
DOI_ORG = 'http://dx.doi.org/'

BIBTEX_TMP = r"""
@%(PT)s{%(KEY)s,
Author = {%(AU)s},
Title = {%(TI)s},
Year = {%(YR)s},
Journal = {%(JN)s},
Number = {%(NU)s},
Pages = {%(PG)s},
Volume = {%(VOL)s}}
"""


def read_records(fname):
    """ Load records from disk

    Parameters
    ----------
    fname : string
        absolute path to the file to be loaded.

    Returns
    -------
    recs : isinstance of pymed.Records
    """
    loaded = json.load(open(fname), object_hook=PubmedRecord)
    return Records(loaded)


def write_records(records, fname, mode='w', indent=None,
                  separators=None):
    """ Save records to json file

    Parameters
    ----------
    records : instance of pymed.Records
        The records to be saved
    fname : str
        The name of the file.
    mode : str
        The mode of the file handler. Should be 'w', 'wb', 'a' 'ab'.
    indent : int | None
        The indentation to use. If None, it defaults to 4.
    separators : tuple
        The separators to be used for elements and mappings.
    """
    if indent is None:
        indent = 4
    if separators is None:
        separators = (',', ': ')

    records = [r for i, r in enumerate(records) if i not in records.exclude_]
    json.dump(records, open(fname, mode), indent=indent,
              separators=separators)


def _bibtex_get_author(author_list):
    """Aux Function"""
    out = []
    for author in author_list:
        names = author.split(' ')
        if len(names) == 2:
            name, surname = names
        elif len(names) >= 2:
            name = ' '.join(names[:len(names) - 1])
            surname = names[-1]
        out += ['%s, %s' % (name, '.'.join(surname))]

    return ' and '.join(out)


def _bibtex_make_id(author, journal, year):
    """Aux Function"""
    fmt = (''.join(c for c in author[0].split(' ')[0].lower() if c.isalpha()),
           str(year))
    return ':'.join(fmt)


def _bibtex_get_pages(pages_str):
    """Aux Function"""
    if PMD.SEP_PAGES_ENTRY in pages_str:
        pages_str = pages_str.split(PMD.SEP_PAGES_ENTRY)[0]
    if '-' in pages_str:
        pfrom, pto = [int(k) for k in pages_str.split(PMD.SEP_PAGES_RANGE)]
        if pfrom > pto:
            pto += pfrom
        pages_str = PMD.SEP_PAGES_RANGE.join([str(k) for k in [pfrom, pto]])

    return pages_str


def _bibtex_get_publication_type(ins):
    """Aux Function"""
    out = 'article'
    # XXX currently only article supported.
    return out


def _make_chunks(n, iterable, padvalue=None):
    """Aux Function: create chunks"""
    return izip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


def _get_doi(rec):
    """Aux Function"""
    doi = rec.get('AID', rec.get('SO',  rec.get('LID', None)))
    if isinstance(doi, list):
        doi = ''.join([d for d in doi if 'doi' in d])
    if doi is not None:
        res = re.findall(DOI_REGEX, doi)
        if res:
            return res[0]


def resolve_doi(rec):
    """Resolve the doi of a given record"""
    doi = _get_doi(rec)
    if doi is not None:
        res = None
        try:
            res = urlopen(DOI_ORG + doi)
        except HTTPError as e:
            res = e
        return res.url


def _export_records(records, fname, end, method):
    """Aux Function"""
    if not fname.endswith(end):
        fname += end
    with open(fname, 'w') as fd:
        for ii, rec in enumerate(records):
            if ii not in records.exclude_:
                fd.write(getattr(rec, method)())


class PubmedRecord(dict):
    """Handle PubMed data

    Note. As the PubMed ID is unique instances of PubmedRecord can be used
    As keys in a dict and can be used with set functions. This is useful
    when dealing with a larger number of records.

    Attributes
    ----------
    pubmed_id : str
        The PubMed ID of the record.
    year : int
        The year of the publication.

    Methods
    -------
    as_corpus:
        Creates single string from record values.
    to_ascii:
        Create formatted text from the records for reading and printing.
    to_nbib:
        Create record in Medline format for importing in Bibliography software.
    to_bibtex:
        Create record in BibTex format for importing in Bibliography software.
    get_doi:
        Parse the doi of the article.
    resolve_doi:
        Get the internet location for the article.
    """
    def __init__(self, mapping):
        for k, v in mapping.items():
            self[k] = v

    def as_corpus(self, fields=None):
        """Return record as single string.

        Parameters
        ----------
        fields : list-like | None
            The fields to be included in the corpus. If None,
            defaults to Title, Author and Abstract.
        Returns
        -------
        corpus : str
            The record concatenated as single string.

        """
        corpus = []
        if fields is None:
            fields = ('TI', 'AU', 'AB')
        for k, v in self.iteritems():
            if isinstance(v, list):
                v = ', '.join(v)
            if any([k in fields,
                    fields == 'all']):
                corpus += [v]

        return ''.join(corpus)

    def to_ascii(self, show_fields=('TI', 'AU', 'DP', 'AB'), width=80):
        """pretty print record

        Parameters
        ----------
        show_fields : list-like
            The fields to display.
        inplace : bool
            If True, records are dropped in-place
        width : int
            The number of characters to display in one line.
        """
        print('')
        print('----- %s' % self.pubmed_id)
        for field in show_fields:
            pretty_field = '\n' + PMD[field] + ':\n'
            out = self.get(field, '%s not available for this rec')
            if isinstance(out, list):
                out = ' '.join(out)
            ind = '    '
            out = textwrap.fill(out, width=width,
                                initial_indent=ind,
                                subsequent_indent=ind)
            print(pretty_field + out)

    def match(self, regexp):
        """match the text corpus against a regular expression or substring

        Note . after regexp support in MNE-Python.
        regexp : str
            Regular expression or substring to tell whether a particular
            expression matches characters in a record.
        """
        def is_substring(string):
            for rep in '-_ ':
                string = string.replace(rep, '')
            return string.isalnum()

        r_ = (re.compile('.*%s.*' % regexp if is_substring(regexp)
              else regexp))
        return r_.match(self.as_corpus())

    def to_nbib(self):
        """Export record in Medline format

        Returns
        -------
        nbib_record : str
            The record in Medline format.
        """
        out = '\n\nPMID- ' + self.pubmed_id
        for k, v in self.items():
            if not k == 'PMID':
                if len(k) < 4:
                    k += (' ' * (4 - len(k)))
                if isinstance(v, list):
                    v = ' '.join(v)
                v = textwrap.fill(v, subsequent_indent=(' ' * 6))
                out += '\n' + '- '.join([k, v])
        return out

    def to_bibtex(self):
        """Export record in BibTex format

        Returns
        -------
        bibtex_record : str
            The record in BibTex format.
        """
        fmt = {
            'PT': _bibtex_get_publication_type(self.get('PT', 'NA')),
            'KEY': _bibtex_make_id(self.get('AU', ''), self.get('JT', 'NA'),
                                   self.year),
            'AU': _bibtex_get_author(self.get('AU', 'NA')),
            'TI': self.get('TI', 'NA'),
            'JN': self.get('JT', 'NA').replace('&', '\&'),
            'YR': '%s' % self.year,
            'NU': self.get('IP', 'NA'),
            'VOL': self.get('IV', 'NA'),
            'PG': self.get('PG', 'NA')
        }
        return BIBTEX_TMP % fmt

    def get_pdf(self):
        """Find and download the associated PDF"""
        raise NotImplemented('This functionality is not available at present.')

    def get_doi(self):
        """Check whethe record as doi

        Returns
        -------
        doi : str | None
            The doi associated with the record. If not available,
            None is returned.
        """
        return _get_doi(self)

    def resolve_doi(self):
        """ Get address from doi
        """
        return resolve_doi(self)

    @property
    def pubmed_id(self):
        """ The pubmed ID of the record.
        """
        return self.get('PMID', None)

    @property
    def year(self):
        """ The year of the publication
        """
        dp = self.get('DP')
        return int(dp[:4]) if dp else dp

    def __hash__(self):
        return self.pubmed_id.__hash__()


class Records(list):
    """Process PubMed records

    Note. Records is a subclass of list, hence, for instances of Records
    all list methods are available. However, the list methods semantics
    is slightly adapted to support processing PubMed records.

    These differences can be summarized as follows:
    - the `append` and `extend` methods will only accept iterables of
      PubmedRecord. The same holds true for the `+` and `+=` operators.
    - `pop` modifies the exclude_ attribute if it is not empty so all indices
      remain intact after removing entires.
    - Slicing will return a new instance of Records, but discards the
      `exclude_` attribute.
    - `insert` requires `exclude_` to be empty. This is to prevent funky
      side-effects.

    To access standard list functionality the convenience method `tolist` is
    provided.

    Parameters
    ----------
    records : listlike
        An Instance of Records or a list of PubmedRecord instances.

    """
    def __init__(self, records=None):
        self.exclude_ = []
        if records:
            self.extend(records)

    def browse(self, show_fields=None, inplace=True, width=80):
        """ Browse and drop records

        This method allows to iterate over records, display their contents
        and to make a decision whether to keep the record or not.
        If the user input is `n`, the record will be discarded or marked for
        removal, depending on the parameters passed.
        If the user input is `q`, the procedure halts.

        Parameters
        ----------
        show_fields : list-like
            The fields to display.
        inplace : bool
            If True, records are dropped in-place. If False, the indices
            are added to to the `exclude_` attribute.
        width : int
            The number of characters to display in one line.
        """
        if show_fields is None:
            show_fields = 'AU', 'TI', 'AB',
        remove_idx = []
        for idx, rec in enumerate(self):
            if rec not in self.exclude_:
                rec.to_ascii(show_fields=show_fields, width=width)
                print('\n --> keep this record? (y/n/q)')
                res = input()
                if res == 'n':
                    remove_idx += [idx]
                elif res == 'q':
                    break
        if inplace and self.exclude_:
            self.drop(remove_idx)
        else:
            self.exclude_ = [i for i in remove_idx if i not in self.exclude_]

    def find(self, regexp):
        """Find records for which as substring or regexp matches

        regexp : str
            Regular expression or substring to select particular records. E.g.
            'Brain' will return all records in which this
            substring is contained.
        """
        return Records(r for r in self if r.match(regexp))

    def drop(self):
        """Delete records

        Returns
        -------
        self : instance of pymed.Records
        """
        [self.remove(r) for ii, r in enumerate(self) if ii in self.exclude_]
        self.exclude_ = []

    def save(self, fname, mode='w', indent=None, separators=None):
        """Save records to json file

        Parameters
        ----------
        fname : str
            The name of the file.
        mode : str
            The mode of the file handler. Should be 'w', 'wb', 'a' 'ab'.
        indent : int | None
            The indentation to use. If None, it defaults to 4.
        separators : tuple
            The separators to be used for elements and mappings.
        """
        write_records(self, fname)

    def save_as_bibtex(self, fname):
        """Export records in bibtex file

        Parameters
        ----------
        fname : str
            The name of the file to save the records in.
        """
        _export_records(self, fname, '.bib', 'to_bibtex')

    def save_as_nbib(self, fname):
        """Export records in bibtex file

        Parameters
        ----------
        fname : str
            The name of the file to save the records in.

        """
        _export_records(self, fname, '.nbib', 'to_nbib')

    def tolist(self):
        """Convert records to list

        Returns
        -------
        The records as a list
        """
        return list(self)

    def copy(self):
        """Copy records

        Returns
        -------
        self : instance of pymed.Records
        """
        return deepcopy(self)

    def append(self, value):
        """Append records

        Parameters
        ----------
        value : instance of pymed.PubmedRecord
            A single PubMed record.

        Returns
        -------
        self : instance of pymed.Records
        """
        if not isinstance(value, PubmedRecord):
            raise TypeError('The item to be added must be an instance of '
                            'PubmedRecord.')
        self.insert(len(self), value)

    def extend(self, values):
        """Extend records

        Parameters
        ----------
        values : listlike
            An iterable of single PubMed records.

        Returns
        -------
        self : instance of pymed.Records
        """
        for v in values:
            if not isinstance(v, PubmedRecord):
                raise ValueError('Finder item must be of type Record')
            self.append(v)

    def insert(self, index, record):
        """Insert record

        Parameters
        ----------
        index : int
            The position to insert the record at.
        record : instance of pymed.PubmedRecord
            The PubmedRecord to be inserted.
        """
        if self.exclude_:
            raise RuntimeError('Indices marked for exclusion must be dropped '
                               'before inserting new records. Please check the'
                               ' .exclude_ attribute')
        else:
            list.insert(self, index, record)

    def pop(self, index):
        """Remove and return record

        Parameters
        ----------
        index : int
            The position of the record to be popped.

        Returns
        -------
        pmd : instance of pymed.PubmedRecord
            The PubMed record to be removed.
        """
        if index in self.exclude_:
            self.exclude_.remove(index)
        return list.pop(self, index)

    def __repr__(self):
        """ Summarize Records """
        out = '<Records | %i entries' % len(self)
        if self:
            minyear = min(r.year for r in self)
            maxyear = max(r.year for r in self)
            if minyear == maxyear:
                yrange = str(minyear)
            else:
                yrange = ' | %i - %i' % (maxyear, minyear)
        else:
            yrange = ''
        return out + '%s>' % yrange

    def __add__(self, other):
        """Add different instances of Records"""
        if not isinstance(other, Records):
            raise TypeError('Only instances of Records can be added together.')
        return Records(list.__add__(self, other))

    def __iadd__(self, values):
        """Append Operator"""
        if not isinstance(values, Records):
            raise TypeError('Only instances of Records can be added together.')
        self.extend(values)
        return self

    def __getslice__(self, *args):
        """Slicing operator"""
        return Records(list.__getslice__(self, *args))


def query_records(term, client, pubmed_fields='all', chunksize=50):
    """Get records from PubMed search

    Parameters
    ----------
    term : string
        The search term.
    client : string
        the user's email address (important for not getting blocked).
    pubmed_fields: list-like
        PubMed fields to constrain the search to.
    chunksize : integer
        size of the searches per query. In case the query fails, try
            using a slightly lower chunk size.

    Returns
    -------
    recs : instance of pymed.Records
    """
    if pubmed_fields is None:
        pubmed_fields = PMD.DEF_FIELDS

    print('Starting query.')
    print('... please be patient. This may take some time.')

    Entrez.email = client
    handle = Entrez.egquery(term=term)  # create handle
    record = Entrez.read(handle)  # launch search an return records
    _retmax = sum(int(r['Count']) for r in record['eGQueryResult']
                  if r['DbName'] == 'pubmed')

    print('... %i records found.' % _retmax)
    print('... downloading records.')
    handle = Entrez.esearch(db='pubmed', term=term,
                            retmax=str(_retmax),
                            usehistory='n')  # create another handle

    hit = Entrez.read(handle)  # parse pubmed IDs...
    id_list = list(hit['IdList'])
    if not id_list:
        print(r"I couldn't find anything")

    chunks = _make_chunks(chunksize, id_list, '')

    def match(key):
        if isinstance(pubmed_fields, list):
            return True if key in pubmed_fields else False
        elif pubmed_fields == 'all':
            return True
        else:
            return RuntimeError('No instruction how to select fields.')

    recs = Records()
    while True:
        chunk = next(chunks, 0)
        if chunk == 0:  # initialize end
            break
        elif not chunk:  # iterate through trailing block.
            chunk = [ch for ch in chunk if ch]
        handle = Entrez.efetch(db='pubmed', id=','.join(chunk),
                               rettype='medline', retmode='text')
        for rec in Medline.parse(handle):
            recs.append(PubmedRecord(dict((k, v) for k, v in rec.items()
                        if match(k))))

    print('Ready.')
    return recs
