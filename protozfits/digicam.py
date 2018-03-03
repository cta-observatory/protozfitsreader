import warnings
import numpy as np
from astropy.utils.decorators import lazyproperty

from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
from .simple import File
from .patch_ids import PATCH_ID_INPUT_SORT_IDS, PATCH_ID_OUTPUT_SORT_IDS
from .any_array_to_numpy import any_array_to_numpy


def event_source(path, run_id=0):
    for event in File(path).Events:
        yield Event(event, run_id)


class Event:
    _sort_ids = None

    def __init__(self, event, run_id):
        if type(type(event)) is GeneratedProtocolMessageType:
            trafo = any_array_to_numpy
        else:
            trafo = no_trafo

        self.run_id = run_id
        self._event = event

        self.pixel_ids = trafo(
            self._event.hiGain.waveforms.pixelsIndices)
        if Event._sort_ids is None:
            Event._sort_ids = np.argsort(self.pixel_ids)
        self.n_pixels = len(self.pixel_ids)
        self._samples = (
            trafo(self._event.hiGain.waveforms.samples)
        ).reshape(self.n_pixels, -1)
        self.baseline = self.unsorted_baseline[Event._sort_ids]
        self.telescope_id = self._event.telescopeID
        self.event_number = self._event.eventNumber
        self.central_event_gps_time = (
            self._event.trig.timeSec * 1E9 + self._event.trig.timeNanoSec
        )
        self.local_time = (
            self._event.local_time_sec * 1E9 + self._event.local_time_nanosec
        )
        self.event_number_array = self._event.arrayEvtNum
        self.camera_event_type = self._event.event_type
        self.array_event_type = self._event.eventType
        self.num_gains = self._event.num_gains
        self.num_channels = self._event.head.numGainChannels
        self.num_samples = self._samples.shape[1]
        self.pixel_flags = trafo(
            self._event.pixels_flags)[Event._sort_ids]
        self.adc_samples = self._samples[Event._sort_ids]
        self.trigger_output_patch7 = _prepare_trigger_output(
            trafo(self._event.trigger_output_patch7))
        self.trigger_output_patch19 = _prepare_trigger_output(
            trafo(self._event.trigger_output_patch19))
        self.trigger_input_traces = _prepare_trigger_input(
            trafo(self._event.trigger_input_traces))

    @lazyproperty
    def unsorted_baseline(self):
        try:
            return any_array_to_numpy(self._event.hiGain.waveforms.baselines)
        except ValueError:
            warnings.warn((
                "Could not read `hiGain.waveforms.baselines` for event:{0}"
                "of run_id:{1}".format(self.event_number, self.run_id)
                ))
            return np.ones(len(self.pixel_ids)) * np.nan


def _prepare_trigger_input(_a):
    A, B = 3, 192
    cut = 144
    _a = _a.reshape(-1, A)
    _a = _a.reshape(-1, A, B)
    _a = _a[..., :cut]
    _a = _a.reshape(_a.shape[0], -1)
    _a = _a.T
    _a = _a[PATCH_ID_INPUT_SORT_IDS]
    return _a


def _prepare_trigger_output(_a):
    A, B, C = 3, 18, 8

    _a = np.unpackbits(_a.reshape(-1, A, B, 1), axis=-1)
    _a = _a[..., ::-1]
    _a = _a.reshape(-1, A*B*C).T
    return _a[PATCH_ID_OUTPUT_SORT_IDS]


def no_trafo(value):
    return value
