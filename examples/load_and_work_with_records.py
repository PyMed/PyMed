# Author: Denis A. Engemann, email: denis.engemann@gmail.com
#
# License: BSD (3-clause)

"""
=========================================
Load and process previously saved records
=========================================

In this example previously downloaded records will be loaded.
Subsequently unwatned records will be discared and finally
the remaining records will be exported in the BibTex format.
"""
print __doc__

import pymed as pm

# load records
recs = pm.read_records('sample_records_dki.json')

# Our recs object is a subclass of list, we can pop, extend, append, insert.
# e.g. remove last record.
recs.pop(-1)

# The elements of `recs` are instances of pymed.PubmedRecord,
# as subclass of dict, and support methods and features that come in handy
# for exploring data ...

# ... read one record
print recs[12].to_ascii(width=100)

# ... resolve digital object identifier of record
# (requires network connection).
# print recs[12].resolve_doi()

# ... print record in BibTex format
print recs[12].to_bibtex()

# but also for filtering
# ... get the publication year as integer
print recs[12].year

# ... get contents as corpus (concatenated as one string)
# this is particularly useful for search in terms in records.
print recs[12].as_corpus()

# We will now make use this to filter out the relevant records.
# In our example these are the ones with complete abstracts
# and `brain` mentioned somewhere in the text.
recs = pm.Records(r for r in recs if 'AB' in r and r.match('brain'))
print recs

# ... now we will remove all records published before 2010.
# Note. the filter method will operat in-place, unless the copy
# parameter is set to `True` (default is `False`).
recs = pm.Records(r for r in recs if r.year > 2010)
print recs

# Because of the PubMed ID records are unique and can therefore be hashed.
# We thus can use set operations to work with records.
# In the following example we will create two overlapping collections
# using random indices and then apply set operations to uniquely combine them.
n_rec = len(recs)

import numpy as np
inds1, inds2, = np.random.randint(n_rec / 2, size=(2, n_rec))
recs1 = pm.Records(rec for ii, rec in enumerate(recs) if ii in inds1)
recs2 = pm.Records(rec for ii, rec in enumerate(recs) if ii in inds2)

# Print records together
print pm.Records(recs1 + recs2)

# Now print unique records.
print pm.Records(set(recs1 + recs2))


# Uncomment the following line to read through your records and discard
# uninteresting ones. Hit 'n' to drop, hit any other key to see the next
# record.

# recs.browse()

# Finally we can export the records to a BibRex file. Another valid choice is
# the Medline nbib format using he `save_as_nbib` method.
recs.save_as_bibtex('mybib.bib')
