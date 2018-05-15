from pkg_resources import resource_string

# imports formerly done in digicam.py
from os.path import isfile
import warnings
import numpy as np
from astropy.utils.decorators import lazyproperty

from . import rawzfitsreader
from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
from .patch_ids import PATCH_ID_INPUT_SORT_IDS, PATCH_ID_OUTPUT_SORT_IDS
from .any_array_to_numpy import any_array_to_numpy
from .L0_pb2 import CameraEvent
# end of imports from digicam.py

from .simple import File as SimpleFile
from .any_array_to_numpy import any_array_to_numpy
from .simple import make_namedtuple

__version__ = resource_string('protozfits', 'VERSION').decode().strip()


__all__ = [
    'SimpleFile',
    'make_namedtuple',
    'any_array_to_numpy',
]
