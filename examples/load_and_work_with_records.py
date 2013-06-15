# Author: Denis A. Engemann, email: denis.engemann@gmail.com
#
# License: BSD (3-clause)

"""

Load and Process Previously Saved Records
-----------------------------------------

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

# ... resolve digitital object identifier of record
# (requires internet connection).
# print recs[12].resolve_doi()

# ... print record in BibTex format
print recs[12].to_bibtex()

# but also for filtering
# ... get the publication year as integer
print recs[12].year

# ... get contents as corpus (concatenated as one string)
# this is particularly useful for searchin terms in records.
print recs[12].as_corpus()

# We will now make use this to filter out the relevant records.
# In our example these are the ones with complete abstracts
# and `brain` mentioned somewhere in the text.
recs = pm.Records(r for r in recs if 'AB' in r and 'brain' in r.as_corpus())
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

# To read and keep / drop single records in a more manually controlled fashion
# consider the browse function. It iterates ove the records, beautifully prints
# the contents and awaits input as to whether keep the reocrd or not.
# Uncommeny the following line to explore.

# recs.browse()

# Finally we can export the records to a BibRex file. Another valid choice is
# the Medline nbib format using he `save_as_nbib` method.
recs.save_as_bibtex('mybib.bib')
