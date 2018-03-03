from pkg_resources import resource_string
from .digicam import File as DigicamFile
from .simple import File as SimpleFile
from .any_array_to_numpy import any_array_to_numpy
from .simple import make_namedtuple

__version__ = resource_string('protozfits', 'VERSION').decode().strip()


__all__ = [
    'DigicamFile',
    'SimpleFile',
    'make_namedtuple',
    'any_array_to_numpy',
]
