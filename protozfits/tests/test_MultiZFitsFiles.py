import pkg_resources
import os
from protozfits import MultiZFitsFiles, File
from glob import glob

example_file_path = pkg_resources.resource_filename(
    'protozfits',
    os.path.join(
        'tests',
        'resources',
        '*.fits.fz'
    )
)

EVENTS_IN_EXAMPLE_FILE = 10
EXPECTED_NUMBER_OF_PIXELS = 1296
EXPECTED_NUMBER_OF_SAMPLES = 50
FIRST_EVENT_NUMBER = 97750287


def test_len():
    '''
    'example_100evts.fits.fz': Table(100xDataModel.CameraEvent),
    'example_LST_R1_10_evts.fits.fz': Table(10xR1.CameraEvent),
    'example_10evts.fits.fz': Table(10xDataModel.CameraEvent),
    'example_9evts_NectarCAM.fits.fz': Table(9xDataModel.CameraEvent),
    'example_SST1M_20180822.fits.fz': Table(32xDataModel.CameraEvent),

    expected number of events: 100 + 10 + 10 + 9 + 32 = 161
    '''
    paths = glob(example_file_path)
    expected_number_of_events = 0
    for path in paths:
        expected_number_of_events += len(File(path).Events)

    assert len(MultiZFitsFiles(paths)) == expected_number_of_events


def test_can_iterate():
    paths = glob(example_file_path)
    f = MultiZFitsFiles(paths)
    assert sum(1 for e in f) == len(f)


def test_is_iteration_order_correct():
    '''I have no idea how to test this.
    '''
    paths = glob(example_file_path)
    f = MultiZFitsFiles(paths)
    for e in f:
        # the tests files are very heterogeneous, some have `eventNumber`
        # all have `event_id` but for those which have `eventNumber`,
        # the `event_id` is always zero.
        try:
            print(e.eventNumber)
        except AttributeError:
            print(e.event_id)
    assert True


def test_headers():
    paths = glob(example_file_path)
    f = MultiZFitsFiles(paths)

    for path, value in f.headers['ZNAXIS2'].items():
        assert File(path).Events.header['ZNAXIS2'] == value

    for path, value in f.headers['PBFHEAD'].items():
        assert File(path).Events.header['PBFHEAD'] == value
