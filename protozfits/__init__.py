from os.path import isfile
import numpy as np
from . import rawzfitsreader
import warnings
from pkg_resources import resource_string

from . import L0_pb2
from .any_array_to_numpy import any_array_to_numpy
from .digicam import _prepare_trigger_input, _prepare_trigger_output

__version__ = resource_string('protozfits', 'VERSION').decode().strip()


class ZFile:

    def __init__(self, fname):
        if not isfile(fname):
            raise FileNotFoundError(fname)
        self.fname = fname
        rawzfitsreader.open(self.fname + ":Events")
        self.numrows = rawzfitsreader.getNumRows()
        self.run_id = 0

    def __iter__(self):
        return self

    def __next__(self):
        event = L0_pb2.CameraEvent()
        try:
            event.ParseFromString(rawzfitsreader.readEvent())
            return Event(event, self.run_id)
        except EOFError:
            raise StopIteration

    def list_tables(self):
        return rawzfitsreader.listAllTables(self.fname)

    def rewind_table(self):
        # Rewind the current reader. Go to the beginning of the table.
        rawzfitsreader.rewindTable()


class Event:
    def __init__(self, event, run_id):
        self.run_id = run_id
        self._event = event

        _e = self._event                   # just to make lines shorter
        _w = self._event.hiGain.waveforms  # just to make lines shorter

        self.pixel_ids = any_array_to_numpy(_w.pixelsIndices)
        self._sort_ids = np.argsort(self.pixel_ids)
        self.n_pixels = len(self.pixel_ids)
        self._samples = any_array_to_numpy(_w.samples).reshape(self.n_pixels, -1)
        self.baseline = self.unsorted_baseline[self._sort_ids]
        self.telescope_id = _e.telescopeID
        self.event_number = _e.eventNumber
        self.central_event_gps_time = self.__calc_central_event_gps_time()
        self.local_time = self.__calc_local_time()
        self.event_number_array = _e.arrayEvtNum
        self.camera_event_type = _e.event_type
        self.array_event_type = _e.eventType
        self.num_gains = _e.num_gains
        self.num_channels = _e.head.numGainChannels
        self.num_samples = self._samples.shape[1]
        self.pixel_flags = any_array_to_numpy(_e.pixels_flags)[self._sort_ids]
        self.adc_samples = self._samples[self._sort_ids]
        self.trigger_output_patch7 = _prepare_trigger_output(
            any_array_to_numpy(_e.trigger_output_patch7))
        self.trigger_output_patch19 = _prepare_trigger_output(
            any_array_to_numpy(_e.trigger_output_patch19))
        self.trigger_input_traces = _prepare_trigger_input(
            any_array_to_numpy(_e.trigger_input_traces))

    @property
    def unsorted_baseline(self):
        if not hasattr(self, '__unsorted_baseline'):
            try:
                self.__unsorted_baseline = any_array_to_numpy(
                    self._event.hiGain.waveforms.baselines)
            except ValueError:
                warnings.warn((
                    "Could not read `hiGain.waveforms.baselines` for event:{0}"
                    "of run_id:{1}".format(self.event_number, self.run_id)
                    ))
                self.__unsorted_baseline = np.ones(
                    len(self.pixel_ids)
                ) * np.nan
        return self.__unsorted_baseline

    def __calc_central_event_gps_time(self):
        time_second = self._event.trig.timeSec
        time_nanosecond = self._event.trig.timeNanoSec
        return time_second * 1E9 + time_nanosecond

    def __calc_local_time(self):
        time_second = self._event.local_time_sec
        time_nanosecond = self._event.local_time_nanosec
        return time_second * 1E9 + time_nanosecond
