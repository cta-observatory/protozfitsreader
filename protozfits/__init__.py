from pkg_resources import resource_string

# this import is *not* needed here, but we get a SegFault! on MAC OSX
# when we do not import it here. I have no idea why.
from . import rawzfitsreader

from .simple import File as SimpleFile
from .any_array_to_numpy import any_array_to_numpy
from .simple import make_namedtuple

__version__ = resource_string('protozfits', 'VERSION').decode().strip()


__all__ = [
    'SimpleFile',
    'make_namedtuple',
    'any_array_to_numpy',
]
