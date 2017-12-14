import pytest
import numpy as np
import pkg_resources
import os

example_file_path = pkg_resources.resource_filename(
    'protozfitsreader',
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
EXPECTED_NUMBER_OF_PIXELS = 1296
EXPECTED_NUMBER_OF_SAMPLES = 50

def to_numpy(a):
    any_array_type_to_npdtype = {
        1: 'i1',
        2: 'u1',
        3: 'i2',
        4: 'u2',
        5: 'i4',
        6: 'u4',
        7: 'i8',
        8: 'u8',
        9: 'f4',
        10: 'f8',
    }

    any_array_type_cannot_convert_exception_text = {
        0: "This any array has no defined type",
        11: """I have no idea if the boolean representation
            of the anyarray is the same as the numpy one"""
    }
    if a.type in any_array_type_to_npdtype:
        return np.frombuffer(
            a.data, any_array_type_to_npdtype[a.type])
    else:
        raise ValueError(
            "Conversion to NumpyArray failed with error:\n%s",
            any_array_type_cannot_convert_exception_text[a.type])


def test_rawreader_can_work_with_relative_path():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    relative_test_file_path = os.path.relpath(example_file_path)
    rawzfitsreader.open(relative_test_file_path + ':Events')
    raw = rawzfitsreader.readEvent()
    assert rawzfitsreader.getNumRows() == EVENTS_IN_EXAMPLE_FILE

    event = L0_pb2.CameraEvent()
    event.ParseFromString(raw)


def test_examplefile_has_no_runheader():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':RunHeader')

    raw = rawzfitsreader.readEvent()
    assert raw < 0

    header = L0_pb2.CameraRunHeader()
    with pytest.raises(TypeError):
        header.ParseFromString(raw)


def test_rawreader_can_work_with_absolute_path():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    raw = rawzfitsreader.readEvent()
    assert rawzfitsreader.getNumRows() == EVENTS_IN_EXAMPLE_FILE

    event = L0_pb2.CameraEvent()
    event.ParseFromString(raw)


def test_rawreader_can_iterate():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())


def test_event_has_certain_fields():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    '''
    The L0_pb2.CameraEvent has many fields, and sub fields.
    However many of them seem to be not used at the moment in SST1M
    So I check if these fields are non empty, since I have seen them used
    in code

        event.eventNumber
        event.telescopeID
        event.trig.timeSec
        event.trig.timeNanoSec
        event.local_time_sec
        event.local_time_nanosec
        event.event_type
        event.eventType
        event.head.numGainChannels
        event.hiGain.waveforms
        event.trigger_input_traces
        event.trigger_output_patch7
        event.trigger_output_patch19
        event.pixels_flags
    '''

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())

        assert event.eventNumber is not None
        assert event.telescopeID is not None
        assert event.head.numGainChannels is not None

        assert event.local_time_sec is not None
        assert event.local_time_nanosec is not None

        assert event.trig.timeSec is not None
        assert event.trig.timeNanoSec is not None

        assert event.event_type is not None
        assert event.eventType is not None

        assert event.hiGain.waveforms is not None
        assert event.hiGain.waveforms.baselines is not None
        assert event.pixels_flags is not None

        assert event.trigger_input_traces is not None
        assert event.trigger_output_patch7 is not None
        assert event.trigger_output_patch19 is not None


#  from this point on, we test not the interface, but that the values
#  are roughly what we expect them to be

def test_eventNumber():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        assert event.eventNumber == i + FIRST_EVENT_IN_EXAMPLE_FILE


def test_telescopeID():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        assert event.telescopeID == TELESCOPE_ID_IN_EXAMPLE_FILE


def test_numGainChannels():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        assert event.head.numGainChannels == -1


def test_local_time():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        local_time = event.local_time_sec * 1e9 + event.local_time_nanosec
        assert local_time == EXPECTED_LOCAL_TIME[i]


def test_trigger_time():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        local_time = event.trig.timeSec * 1e9 + event.trig.timeNanoSec
        assert local_time == 0


def test_event_type():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        assert event.event_type == [1, 1, 1, 1, 1, 8, 1, 1, 1, 1][i]


def test_eventType():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        assert event.eventType == 0


def test_waveforms():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())
        waveforms = to_numpy(event.hiGain.waveforms)
        N = EXPECTED_NUMBER_OF_PIXELS * EXPECTED_NUMBER_OF_SAMPLES
        assert waveforms.shape == (N, )
        assert waveforms.dtype == np.int16
        assert waveforms.min() >= 0
        assert waveforms.max() <= (2**12) - 1


def test_baselines():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())

        baselines = to_numpy(event.hiGain.waveforms.baselines)
        assert baselines.shape == (EXPECTED_NUMBER_OF_PIXELS, )
        assert baselines.dtype == np.int16
        assert baselines.min() >= 0
        assert baselines.max() <= (2**12) - 1


def test_pixel_flags():
    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())

        pixel_flags = to_numpy(event.pixels_flags)
        assert len(pixel_flags) == EXPECTED_NUMBER_OF_PIXELS
        assert pixel_flags.dtype == np.uint16


def test_trigger_related_arrays():

    from protozfitsreader import rawzfitsreader
    from protozfitsreader import L0_pb2

    rawzfitsreader.open(example_file_path + ':Events')
    for i in range(rawzfitsreader.getNumRows()):
        event = L0_pb2.CameraEvent()
        event.ParseFromString(rawzfitsreader.readEvent())

        for field_under_test in [
            event.trigger_input_traces,
            event.trigger_output_patch7,
            event.trigger_output_patch19,
        ]:
            array_under_test = to_numpy(field_under_test)
            assert array_under_test.shape == (432 * 50, )
            assert array_under_test.dtype == np.uint8
