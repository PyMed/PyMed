"""Some utility functions"""

# Authors: Denis A. Engemann <denis.engeman@gmail.com>
#
# License: BSD (3-clause)

import tempfile
import atexit
from shutil import rmtree


class _TempDir(str):
    """Class for creating and auto-destroying temp dir

    Note. copied from mne-python

    This is designed to be used with testing modules.

    We cannot simply use __del__() method for cleanup here because the rmtree
    function may be cleaned up before this object, so we use the atexit module
    instead. Passing del_after and print_del kwargs to the constructor are
    helpful primarily for debugging purposes.
    """
    def __new__(self, del_after=True, print_del=False):
        new = str.__new__(self, tempfile.mkdtemp())
        self._del_after = del_after
        self._print_del = print_del
        return new

    def __init__(self):
        self._path = self.__str__()
        atexit.register(self.cleanup)

    def cleanup(self):
        if self._del_after is True:
            if self._print_del is True:
                print 'Deleting %s ...' % self._path
            rmtree(self._path, ignore_errors=True)
