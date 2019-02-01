import os
import pytest
import pkg_resources
import numpy as np

from protozfits import File, isnamedtupleinstance
from protozfits.R1_pb2 import CameraConfiguration
from protozfits.R1_pb2 import CameraEvent as R1_Cam_Event
from protozfits.L0_pb2 import CameraRunHeader
from protozfits.L0_pb2 import CameraEvent as L0_Cam_Event

EXAMPLE_PATH = pkg_resources.resource_filename(
    'protozfits',
    os.path.join(
        'tests',
        'resources',
        'example_10evts.fits.fz'
    )
)


def test_get_cpp_msg_type_name():
    from protozfits import cpp_message_type

    classes_expected_results = {
        CameraConfiguration: 'R1_CAMERA_CONFIG',
        R1_Cam_Event: 'R1_CAMERA_EVENT',
        CameraRunHeader: 'DL0_RUN_HEADER',
        L0_Cam_Event: 'DL0_CAMERA_EVENT',
    }

    for cls, expected_result in classes_expected_results.items():
        e = cls()
        msg_type = cpp_message_type(e)
        assert msg_type == expected_result


def test_open_no_with(tmpdir):
    from protozfits import FileWriter
    path = tmpdir.join("open_no_with.fits.fz")
    print('\n path:', path)
    outfile = FileWriter(path)
    outfile.close()


def test_open_with_with(tmpdir):
    from protozfits import FileWriter
    path = tmpdir.join("open_with_with.fits.fz")
    print('\n path:', path)
    with FileWriter(path) as _:
        pass


def test_writer_10_R1_cam_events(tmpdir):
    from protozfits import FileWriter

    path = tmpdir.join("writer_10_R1_cam_events.fits.fz")
    print('\n path:', path)
    with FileWriter(path) as outfile:

        for i in range(10):
            test_event = R1_Cam_Event()
            test_event.event_id = i
            outfile.append(test_event)


@pytest.fixture
def little_test_file(tmpdir):
    from protozfits import FileWriter

    path = str(tmpdir.join("little_test_file.fits.fz"))
    print('\n path:', path)
    with FileWriter(path) as outfile:

        for i in range(10):
            test_event = R1_Cam_Event()
            test_event.event_id = i
            outfile.append(test_event)

    return path


def test_write_and_read(little_test_file):
    from protozfits import File

    with File(little_test_file) as infile:
        for i, event in enumerate(infile.Events):
            assert event.event_id == i


def compare_named_tuples(a, b):
    '''helper to recursively compare nested namedtuples containing np.arrays
    '''
    for k in a._fields:
        ai = getattr(a, k)
        bi = getattr(b, k)
        if isnamedtupleinstance(ai):
            compare_named_tuples(ai, bi)
        else:
            assert np.all(ai == bi)


def test_copy_a_file(tmpdir):
    from protozfits import FileWriter

    path = str(tmpdir.join("copy_of_a_file.fits.fz"))
    print('\n path:', path)

    # make the copy
    with File(EXAMPLE_PATH) as infile:
        with FileWriter(path) as outfile:
            for event in infile.Events:
                outfile.append(event)

    # read copy and original and compare them.
    with File(EXAMPLE_PATH) as original:
        with File(path) as copy:
            for a, b in zip(original.Events, copy.Events):
                compare_named_tuples(a, b)
