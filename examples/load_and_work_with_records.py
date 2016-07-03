# Author: Denis A. Engemann <denis.engemann@gmail.com>
#
# License: BSD (3-clause)

"""
=========================================
Load and process previously saved records
=========================================

In this example previously downloaded records will be loaded.
We explore how to access and print single records.
Subsequently, we will explore filtering and combining records.
A last section shows how to save and export results for usage
with bibliographic software.

"""
import pymed as pm
import numpy as np

print(__doc__)

# load records
recs = pm.read_records('sample_records_dki.json')

###############################################################################
# Access records in different ways

# ... read one record, nicely printed.
print(recs[12].to_ascii(width=100))

# ... get the publication year as integer
print(recs[12].year)

# ... get contents as corpus (concatenated as one string)
# this is particularly useful for search in terms in records.
print(recs[12].as_corpus())

# ... resolve digital object identifier of a record
# (requires network connection --- uncomment if you're connected).
# print recs[12].resolve_doi()

# Uncomment the following line to read through your records and discard
# uninteresting ones. Hit 'n' to drop, hit any other key to see the next
# record.

# recs.browse()

# Note. records are special cases of lists and a single records are special
# cases of dictionaries.

last_rec = recs.pop(-1)
print(last_rec.keys())

###############################################################################
# Filter and combine records

# get all records that have an abstract and are related to brains.
recs = pm.Records(r for r in recs if 'AB' in r and r.match('brain'))
print(recs)

# remove all records published before 2010.
recs = pm.Records(r for r in recs if r.year > 2010)
print(recs)

# Because of the PubMed ID records are unique and can therefore be hashed.
# This means you can use records as keys in dictionaries or use set logic
# to remove duplicates, take differences, etc.
# In the following example we will create two overlapping collections
# using random indices and then apply set operations to uniquely combine them.
n_rec = len(recs)

inds1, inds2, = np.random.randint(n_rec / 2, size=(2, n_rec))
recs1 = pm.Records(rec for ii, rec in enumerate(recs) if ii in inds1)
recs2 = pm.Records(rec for ii, rec in enumerate(recs) if ii in inds2)

# Now print unique records.
print(pm.Records(set(recs1 + recs2)))

###############################################################################
# Save and export results.

# Finally we can export the records to a BibTex file. Another valid choice is
# the Medline nbib format using he `save_as_nbib` method.

# ... print single record in BibTex format
print(recs[12].to_bibtex())

# ... save all records
recs.save_as_bibtex('mybib.bib')
