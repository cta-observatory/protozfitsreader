
import numpy as np
import pkg_resources
import os

example_file_path = pkg_resources.resource_filename(
    'protozfits',
    os.path.join(
        'tests',
        'resources',
        'example_LST_R1_10_evts.fits.fz'
    )
)


def test_can_open_file():
    from protozfits import File
    File(example_file_path)


def test_can_iterate_over_events_and_run_header():
    from protozfits import File
    f = File(example_file_path)

    camera_config = next(f.CameraConfig)
    assert (camera_config.expected_pixels_id == np.arange(14)).all()

    for event in f.Events:
        assert event.waveform.shape == (1120,)
        assert event.pixel_status.shape == (14,)
        assert event.lstcam.first_capacitor_id.shape == (16,)
        assert event.lstcam.counters.shape == (44,)
