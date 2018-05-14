import numpy as np
import pkg_resources
import os

from protozfits import SimpleFile

example_file_path = pkg_resources.resource_filename(
    'protozfits',
    os.path.join(
        'tests',
        'resources',
        'example_LST_R1_10_evts.fits.fz'
    )
)


def test_open_example_LST_R1_file():
    f = SimpleFile(example_file_path)
    print('open worked', flush=True)
    f.close()


def test_can_open_a_second_time():
    f = SimpleFile(example_file_path)
    print('open worked', flush=True)
    f.close()


def test_can_print_events_table():
    f = SimpleFile(example_file_path)
    print(f.Events)
    f.close()

"""
def test_can_iterate_over_events_std_form():
    f = SimpleFile(example_file_path)
    for event in f.Events:
        pass
    f.close()


def test_can_iterate_over_events__with_form():
    with SimpleFile(example_file_path) as f:
        for event in f.Events:
            pass


def test_can_iterate_over_events_and_run_header():

    with SimpleFile(example_file_path) as f:

        camera_config = next(f.CameraConfig)
        assert (camera_config.expected_pixels_id == np.arange(14)).all()

        for i, event in enumerate(f.Events):
            assert event.event_id == i + 1
            assert event.waveform.shape == (1120,)
            assert event.pixel_status.shape == (14,)
            assert event.lstcam.first_capacitor_id.shape == (16,)
            assert event.lstcam.counters.shape == (44,)
"""
