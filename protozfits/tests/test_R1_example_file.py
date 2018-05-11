
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
    from protozfits import SimpleFile
    f = SimpleFile(example_file_path)
    f.close()


def test_can_iterate_over_events_and_run_header():
    from protozfits import SimpleFile
    f = SimpleFile(example_file_path)

    camera_config = next(f.CameraConfig)
    assert (camera_config.expected_pixels_id == np.arange(14)).all()

    for event in f.Events:
        assert event.waveform.shape == (1120,)
        assert event.pixel_status.shape == (14,)
        assert event.lstcam.first_capacitor_id.shape == (16,)
        assert event.lstcam.counters.shape == (44,)
    f.close()

def test_event_ids():
    from protozfits import SimpleFile
    with SimpleFile(example_file_path) as f:
        event_ids = [e.event_id for e in f.Events]

    assert (np.array(event_ids) == 1 + np.arange(len(event_ids))).all()
