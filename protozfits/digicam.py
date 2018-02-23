import numpy as np
from astropy.utils.decorators import lazyproperty

from .simple import File
from .patch_ids import PATCH_ID_INPUT, PATCH_ID_OUTPUT


def event_source(path, run_id=0):
    for event in File(path):
        yield Event(event, run_id)


class Event:
    def __init__(self, event, run_id):
        self.run_id = run_id
        self._event = event

        _e = self._event
        _w = self._event.hiGain.waveforms

        self.pixel_ids = _w.pixelsIndices
        self._sort_ids = np.argsort(self.pixel_ids)
        self.n_pixels = len(self.pixel_ids)
        self._samples = _w.samples.reshape(self.n_pixels, -1)
        self.baseline = _w.baselines[self._sort_ids]
        self.telescope_id = _e.telescopeID
        self.event_number = _e.eventNumber
        self.event_number_array = _e.arrayEvtNum
        self.camera_event_type = _e.event_type
        self.array_event_type = _e.eventType
        self.num_gains = _e.num_gains
        self.num_channels = _e.head.numGainChannels
        self.num_samples = self._samples.shape[1]
        self.pixel_flags = _e.pixels_flags[self._sort_ids]
        self.adc_samples = self._samples[self._sort_ids]
        self.trigger_output_patch7 = _prepare_trigger_output(
            _e.trigger_output_patch7)
        self.trigger_output_patch19 = _prepare_trigger_output(
            _e.trigger_output_patch19)
        self.trigger_input_traces = _prepare_trigger_input(
            _e.trigger_input_traces)

    @lazyproperty
    def central_event_gps_time(self):
        time_second = self._event.trig.timeSec
        time_nanosecond = self._event.trig.timeNanoSec
        return time_second * 1E9 + time_nanosecond

    @lazyproperty
    def local_time(self):
        time_second = self._event.local_time_sec
        time_nanosecond = self._event.local_time_nanosec
        return time_second * 1E9 + time_nanosecond


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

