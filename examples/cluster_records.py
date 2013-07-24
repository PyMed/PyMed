# Author: Lars Buitinck <L.J.Buitinck@uva.nl>
#
# License: BSD (3-clause)

"""
================================
Cluster a batch of saved records
================================

This example does some extremely simplistic clustering of
PubMed abstracts. It shows how to tie PyMed to scikit-learn.

Results will vary between runs because the k-means clustering
is initialized randomly.

(Try running this on a larger set for better results.)

"""
print(__doc__)

import numpy as np
import pymed as pm
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# settings
field = 'AB'        # what we want to cluster
n_clusters = 5      # number of clusters
n_components = 50   # components for LSA/SVD

# load records
recs = pm.read_records('sample_records_dki.json')
recs = pm.Records(r for r in recs if field in r)

print("Extracting tf-idf vectors.")
vect = TfidfVectorizer(input="content", ngram_range=(1, 2),
                       stop_words='english', sublinear_tf=True)
tfidf = vect.fit_transform(r[field] for r in recs if field in r)

print("Computing LSA (aka SVD).")
lsa = TruncatedSVD(n_components=n_components).fit_transform(tfidf)
lsa = normalize(lsa)

print("Clustering {} records into {} clusters.".format(len(recs), n_clusters))
# Note that if you have huge numbers of records to cluster,
# sklearn.cluster.MiniBatchKMeans is a better option.
km = KMeans(n_clusters=n_clusters, max_iter=20, n_init=10)

labels = km.fit_predict(tfidf)

for label in np.unique(labels):
    print("")
    cluster = np.where(labels == label)[0]
    print("Cluster {}:".format(label + 1))
    for idx in cluster:
        print("    {}".format(recs[idx]['TI']))
