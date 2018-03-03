from os.path import isfile
from pkg_resources import resource_string
import warnings
import numpy as np

from . import rawzfitsreader
from .L0_pb2 import CameraEvent
from .digicam import Event

__version__ = resource_string('protozfits', 'VERSION').decode().strip()


class ZFile:

    def __init__(self, fname):
        if not isfile(fname):
            raise FileNotFoundError(fname)
        self.fname = fname
        rawzfitsreader.open(self.fname + ":Events")
        self.numrows = rawzfitsreader.getNumRows()
        self.run_id = 0

    def __iter__(self):
        return self

    def __next__(self):
        event = CameraEvent()
        try:
            event.ParseFromString(rawzfitsreader.readEvent())
            return Event(event, self.run_id)
        except EOFError:
            raise StopIteration

    def list_tables(self):
        return rawzfitsreader.listAllTables(self.fname)

    def rewind_table(self):
        # Rewind the current reader. Go to the beginning of the table.
        rawzfitsreader.rewindTable()


