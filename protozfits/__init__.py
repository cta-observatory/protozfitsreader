from pkg_resources import resource_string
from .digicam import File as DigicamFile
from .simple import File as SimpleFile

__version__ = resource_string('protozfits', 'VERSION').decode().strip()


__all__ = [
    'DigicamFile',
    'SimpleFile',
]
