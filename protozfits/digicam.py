import numpy as np
from .simple import File
from .patch_ids import PATCH_ID_INPUT, PATCH_ID_OUTPUT


def event_source(path, run_id=0):
    for event in File(path).Events:
        yield Event(event, run_id)


class Event:
    _sort_ids = None

    def __init__(self, event, run_id):
        self.run_id = run_id
        self._event = event
        self.pixel_ids = self._event.hiGain.waveforms.pixelsIndices
        if Event._sort_ids is None:
            Event._sort_ids = np.argsort(self.pixel_ids)

        self.n_pixels = len(self.pixel_ids)
        self.baseline = self._event.hiGain.waveforms.baselines[Event._sort_ids]
        self.telescope_id = self._event.telescopeID
        self.event_number = self._event.eventNumber
        self.event_number_array = self._event.arrayEvtNum
        self.camera_event_type = self._event.event_type
        self.array_event_type = self._event.eventType
        self.num_gains = self._event.num_gains
        self.num_channels = self._event.head.numGainChannels
        self._samples = self._event.hiGain.waveforms.samples.reshape(
            self.n_pixels, -1)
        self.num_samples = self._samples.shape[1]
        self.pixel_flags = self._event.pixels_flags[Event._sort_ids]
        self.adc_samples = self._samples[Event._sort_ids]
        self.trigger_output_patch7 = _prepare_trigger_output(
            self._event.trigger_output_patch7)
        self.trigger_output_patch19 = _prepare_trigger_output(
            self._event.trigger_output_patch19)
        self.trigger_input_traces = _prepare_trigger_input(
            self._event.trigger_input_traces)
        self.central_event_gps_time = (
            self._event.trig.timeSec * 1e9 + self._event.trig.timeNanoSec
        )
        self.local_time = (
            self._event.local_time_sec * 1e9 + self._event.local_time_nanosec
        )


def _prepare_trigger_input(_a):
    A, B = 3, 192
    cut = 144
    _a = _a.reshape(-1, A)
    _a = _a.reshape(-1, A, B)
    _a = _a[..., :cut]
    _a = _a.reshape(_a.shape[0], -1)
    _a = _a.T
    _a = _a[np.argsort(PATCH_ID_INPUT)]
    return _a


def _prepare_trigger_output(_a):
    A, B, C = 3, 18, 8

    _a = np.unpackbits(_a.reshape(-1, A, B, 1), axis=-1)
    _a = _a[..., ::-1]
    _a = _a.reshape(-1, A*B*C).T
    return _a[np.argsort(PATCH_ID_OUTPUT)]
