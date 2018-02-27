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

        self.pixel_ids = any_array_to_numpy(
            self._event.hiGain.waveforms.pixelsIndices)
        self._sort_ids = np.argsort(self.pixel_ids)
        self.n_pixels = len(self.pixel_ids)
        self._samples = any_array_to_numpy(
            self._event.hiGain.waveforms.samples).reshape(self.n_pixels, -1)
        self.baseline = self.unsorted_baseline[self._sort_ids]
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
        self.pixel_flags = any_array_to_numpy(
            self._event.pixels_flags
        )[self._sort_ids]
        self.adc_samples = self._samples[self._sort_ids]
        self.trigger_output_patch7 = _prepare_trigger_output(
            any_array_to_numpy(self._event.trigger_output_patch7))
        self.trigger_output_patch19 = _prepare_trigger_output(
            any_array_to_numpy(self._event.trigger_output_patch19))
        self.trigger_input_traces = _prepare_trigger_input(
            any_array_to_numpy(self._event.trigger_input_traces))

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
