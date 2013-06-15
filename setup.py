#! /usr/bin/env python
#
# Copyright (C) 2011 Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>

import os
import pymed

import setuptools  # we are using a setuptools namespace
from numpy.distutils.core import setup

descr = """MNE python project for MEG and EEG data analysis."""

DISTNAME            = 'pymed'
DESCRIPTION         = descr
MAINTAINER          = 'Denis A. Engemann'
MAINTAINER_EMAIL    = 'd.engemann@fz-juelich.de'
LICENSE             = 'BSD (3-clause)'
DOWNLOAD_URL        = 'https://github.com/dengemann/pymed.git'
VERSION             = pymed.__version__


if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.rst').read(),
          zip_safe=False,  # the package can run out of an .egg file
          classifiers=['Intended Audience :: Science/Research',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved',
                       'Programming Language :: Python',
                       'Topic :: Software Development',
                       'Topic :: Scientific/Engineering',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX',
                       'Operating System :: Unix',
                       'Operating System :: MacOS'],
          platforms='any',
          packages=['pymed', 'pymed.tests'])