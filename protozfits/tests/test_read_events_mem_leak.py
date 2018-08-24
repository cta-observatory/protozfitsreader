
from itertools import cycle
import pkg_resources
import os

example_file_path = pkg_resources.resource_filename(
    'protozfits',
    os.path.join(
        'tests',
        'resources',
        'example_10evts.fits.fz'
    )
)


def test_zfile_raises_on_wrong_path():

    from protozfits import rawzfitsreader

    for path in zip(cycle(example_file_path), range(100)):
        rawzfitsreader.open(path + ":Events")
        rawzfitsreader.readEvent()
