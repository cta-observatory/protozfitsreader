
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

FIRST_EVENT_IN_EXAMPLE_FILE = 97750287
TELESCOPE_ID_IN_EXAMPLE_FILE = 1
EVENTS_IN_EXAMPLE_FILE = 10
EXPECTED_LOCAL_TIME = [
    1.5094154944067896e+18,
    1.509415494408104e+18,
    1.509415494408684e+18,
    1.509415494415717e+18,
    1.5094154944180828e+18,
    1.5094154944218719e+18,
    1.5094154944245553e+18,
    1.5094154944267853e+18,
    1.509415494438982e+18,
    1.5094154944452902e+18
]
EXPECTED_GPS_TIME = [0] * EVENTS_IN_EXAMPLE_FILE


def test_rawreader_can_work_with_relative_path():
    from protozfits import rawzfitsreader
    from protozfits import L0_pb2

    relative_test_file_path = os.path.relpath(example_file_path)
    rawzfitsreader.open(relative_test_file_path + ':Events')
    raw = rawzfitsreader.readEvent()
    assert rawzfitsreader.getNumRows() == EVENTS_IN_EXAMPLE_FILE

    event = L0_pb2.CameraEvent()
    event.ParseFromString(raw)

"""
def test_examplefile_has_no_runheader():
    from protozfits import rawzfitsreader
    from protozfits import L0_pb2

    rawzfitsreader.open(example_file_path + ':RunHeader')

    raw = rawzfitsreader.readEvent()
    assert raw < 0

    header = L0_pb2.CameraRunHeader()
    with pytest.raises(TypeError):
        header.ParseFromString(raw)
"""

def test_rawreader_can_work_with_absolute_path():
    from protozfits import rawzfitsreader
    from protozfits import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    raw = rawzfitsreader.readEvent()
    assert rawzfitsreader.getNumRows() == EVENTS_IN_EXAMPLE_FILE

    event = L0_pb2.CameraEvent()
    event.ParseFromString(raw)

