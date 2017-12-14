import pytest

import pkg_resources
import os
import warnings

warnings.simplefilter("ignore")

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
        assert event.trigger_input_traces is not None
        assert event.trigger_output_patch7 is not None
        assert event.trigger_output_patch19 is not None
        assert event.pixels_flags is not None


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
        assert event.head.numGainChannels == 0


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


"""

def test_n_pixel():
    from digicampipe.io.protozfitsreader import ZFile
    n_pixel = [
        event.n_pixels
        for event in ZFile(example_file_path)
    ]
    assert n_pixel == [1296] * EVENTS_IN_EXAMPLE_FILE


def test_pixel_flags():
    from digicampipe.io.protozfitsreader import ZFile
    pixel_flags = [
        event.pixel_flags
        for event in ZFile(example_file_path)
    ]
    expected_pixel_flags = [
        np.ones(1296, dtype=np.bool)
    ] * EVENTS_IN_EXAMPLE_FILE

    for actual, expected in zip(pixel_flags, expected_pixel_flags):
        assert (actual == expected).all()



def test_num_samples():
    from digicampipe.io.protozfitsreader import ZFile
    num_samples = [
        event.num_samples
        for event in ZFile(example_file_path)
    ]
    assert num_samples == [50] * EVENTS_IN_EXAMPLE_FILE


def test_adc_samples():
    from digicampipe.io.protozfitsreader import ZFile
    adc_samples = [
        event.adc_samples
        for event in ZFile(example_file_path)
    ]

    for actual in adc_samples:
        assert actual.dtype == np.int16
        assert actual.shape == (1296, 50)

    adc_samples = np.array(adc_samples)

    # these are 12 bit ADC values, so the range must
    # can at least be asserted
    assert adc_samples.min() == 0
    assert adc_samples.max() == (2**12) - 1


def test_trigger_input_traces():
    from digicampipe.io.protozfitsreader import ZFile
    trigger_input_traces = [
        event.trigger_input_traces
        for event in ZFile(example_file_path)
    ]

    for actual in trigger_input_traces:
        assert actual.dtype == np.uint8
        assert actual.shape == (432, 50)


def test_trigger_output_patch7():
    from digicampipe.io.protozfitsreader import ZFile
    trigger_output_patch7 = [
        event.trigger_output_patch7
        for event in ZFile(example_file_path)
    ]

    for actual in trigger_output_patch7:
        assert actual.dtype == np.uint8
        assert actual.shape == (432, 50)


def test_trigger_output_patch19():
    from digicampipe.io.protozfitsreader import ZFile
    trigger_output_patch19 = [
        event.trigger_output_patch19
        for event in ZFile(example_file_path)
    ]

    for actual in trigger_output_patch19:
        assert actual.dtype == np.uint8
        assert actual.shape == (432, 50)


def test_baseline():
    from digicampipe.io.protozfitsreader import ZFile
    baseline = [
        event.baseline
        for event in ZFile(example_file_path)
    ]

    for actual in baseline:
        assert actual.dtype == np.int16
        assert actual.shape == (1296,)

    baseline = np.array(baseline)

    baseline_deviation_between_events = baseline.std(axis=0)
    # I don't know if this is a good test, but I assume baseline should
    # not vary too much between events, so I had a look at these.
    assert baseline_deviation_between_events.max() < 60
    assert baseline_deviation_between_events.mean() < 2
"""
