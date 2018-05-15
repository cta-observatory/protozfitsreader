import pytest

import pkg_resources
import os
import numpy as np

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


def test_zfile_raises_on_wrong_path():
    from protozfits import DigicamFile
    with pytest.raises(FileNotFoundError):
        DigicamFile('foo.bar')


def test_zfile_opens_correct_path():
    from protozfits import DigicamFile
    DigicamFile(example_file_path)


def test_can_iterate_over_events():
    from protozfits import DigicamFile

    for __ in DigicamFile(example_file_path):
        pass


def test_iteration_yield_expected_fields():
    from protozfits import DigicamFile

    for event in DigicamFile(example_file_path):
        # we just want to see, that the zfits file has all these
        # fields and we can access them
        event.telescope_id
        event.num_gains
        event.n_pixels
        event.event_number
        event.pixel_flags

        event.local_time
        event.central_event_gps_time
        event.camera_event_type
        event.array_event_type
        event.num_samples
        event.adc_samples

        # expert mode fields
        event.trigger_input_traces
        event.trigger_output_patch7
        event.trigger_output_patch19
        event.baseline


def test_event_number():
    from protozfits import DigicamFile

    event_numbers = [
        event.event_number
        for event in DigicamFile(example_file_path)
    ]
    expected_event_numbers = [
        FIRST_EVENT_IN_EXAMPLE_FILE + i
        for i in range(EVENTS_IN_EXAMPLE_FILE)
    ]
    assert event_numbers == expected_event_numbers


def test_telescope_ids():
    from protozfits import DigicamFile
    telescope_ids = [
        event.telescope_id
        for event in DigicamFile(example_file_path)
    ]
    expected_ids = [TELESCOPE_ID_IN_EXAMPLE_FILE] * EVENTS_IN_EXAMPLE_FILE
    assert telescope_ids == expected_ids


def test_num_gains():
    from protozfits import DigicamFile
    num_gains = [
        event.num_gains
        for event in DigicamFile(example_file_path)
    ]
    expected_num_gains = [0] * EVENTS_IN_EXAMPLE_FILE
    assert num_gains == expected_num_gains


def test_num_channels():
    from protozfits import DigicamFile
    for event in DigicamFile(example_file_path):
        assert -1 == event.num_channels


def test_n_pixel():
    from protozfits import DigicamFile
    n_pixel = [
        event.n_pixels
        for event in DigicamFile(example_file_path)
    ]
    assert n_pixel == [1296] * EVENTS_IN_EXAMPLE_FILE


def test_pixel_flags():
    from protozfits import DigicamFile
    pixel_flags = [
        event.pixel_flags
        for event in DigicamFile(example_file_path)
    ]
    expected_pixel_flags = [
        np.ones(1296, dtype=np.bool)
    ] * EVENTS_IN_EXAMPLE_FILE

    for actual, expected in zip(pixel_flags, expected_pixel_flags):
        assert (actual == expected).all()


def test_local_time():
    from protozfits import DigicamFile
    local_time = [
        event.local_time
        for event in DigicamFile(example_file_path)
    ]
    assert local_time == EXPECTED_LOCAL_TIME


def test_gps_time():
    from protozfits import DigicamFile
    gps_time = [
        event.central_event_gps_time
        for event in DigicamFile(example_file_path)
    ]
    assert gps_time == EXPECTED_GPS_TIME


def test_camera_event_type():
    from protozfits import DigicamFile
    camera_event_type = [
        event.camera_event_type
        for event in DigicamFile(example_file_path)
    ]
    assert camera_event_type == [1, 1, 1, 1, 1, 8, 1, 1, 1, 1]


def test_array_event_type():
    from protozfits import DigicamFile
    array_event_type = [
        event.array_event_type
        for event in DigicamFile(example_file_path)
    ]
    assert array_event_type == [0] * EVENTS_IN_EXAMPLE_FILE


def test_num_samples():
    from protozfits import DigicamFile
    num_samples = [
        event.num_samples
        for event in DigicamFile(example_file_path)
    ]
    assert num_samples == [50] * EVENTS_IN_EXAMPLE_FILE


def test_adc_samples():
    from protozfits import DigicamFile
    adc_samples = [
        event.adc_samples
        for event in DigicamFile(example_file_path)
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
    from protozfits import DigicamFile
    trigger_input_traces = [
        event.trigger_input_traces
        for event in DigicamFile(example_file_path)
    ]

    for actual in trigger_input_traces:
        assert actual.dtype == np.uint8
        assert actual.shape == (432, 50)


def test_trigger_output_patch7():
    from protozfits import DigicamFile
    trigger_output_patch7 = [
        event.trigger_output_patch7
        for event in DigicamFile(example_file_path)
    ]

    for actual in trigger_output_patch7:
        assert actual.dtype == np.uint8
        assert actual.shape == (432, 50)


def test_trigger_output_patch19():
    from protozfits import DigicamFile
    trigger_output_patch19 = [
        event.trigger_output_patch19
        for event in DigicamFile(example_file_path)
    ]

    for actual in trigger_output_patch19:
        assert actual.dtype == np.uint8
        assert actual.shape == (432, 50)


def test_baseline():
    from protozfits import DigicamFile
    baseline = [
        event.baseline
        for event in DigicamFile(example_file_path)
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
