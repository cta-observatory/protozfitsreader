#!/bin/env python
# this code should run in python3.
# Zfits/protobuf loader.
# import protozfitsreader
import numpy as np
from . import rawzfitsreader
from . import L0_pb2


class ZFile(object):
    def __init__(self, fname):
        self.fname = fname

    def _read_file(self):
        if self.ttype not in ["RunHeader", "Events", "RunTails"]:
            print("Error: Table type not RunHeader, Events or RunTails")
        else:
            rawzfitsreader.open("%s:%s" % (self.fname, self.ttype))

    def _read_message(self):
        '''Read next message.
            Fills property self.rawmessage and self.numrows
        '''
        self.rawmessage = rawzfitsreader.readEvent()
        self.numrows = rawzfitsreader.getNumRows()

    def _extract_field(self, obj, field):
        # Read a specific field in object 'obj' given as input 'field'
        if not obj.HasField(field):
            raise KeyError(str(field))
        return getattr(obj, field)

    def list_tables(self):
        return rawzfitsreader.listAllTables(self.fname)

    def read_runheader(self):
        if not self.ttype == "RunHeader":
            self.ttype = "RunHeader"
            self._read_file()

        self._read_message()
        self.header = L0_pb2.CameraRunHeader()
        self.header.ParseFromString(self.rawmessage)

    def read_event(self):
        if not self.ttype == "Events":
            self.ttype = "Events"
            self._read_file()
            self.eventnumber = 1
        else:
            self.eventnumber += 1

        self._read_message()
        self.event = L0_pb2.CameraEvent()
        self.event.ParseFromString(self.rawmessage)

    def rewind_table(self):
        # Rewind the current reader. Go to the beginning of the table.
        rawzfitsreader.rewindTable()

    def move_to_next_event(self):
        # Iterate over events
        i = 0
        numrows = i+2
        # Hook to deal with file with no header (1)
        if hasattr(self, 'numrows'):
            numrows = self.numrows
        # End - Hook to deal with file with no header (1)

        while i < numrows:
            self.read_event()
            # Hook to deal with file with no header (2)
            if hasattr(self, 'numrows'):
                numrows = self.numrows
            # End - Hook to deal with file with no header (2)

            # Hook to deal with file with no header (3)
            try:
                run_id   = self.get_run_id()
                event_id = self.get_event_id()
            except:
                run_id = 0
                event_id = self.eventnumber
            # Hook to deal with file with no header (3)

            yield run_id, event_id
            i += 1

    def get_telescope_id(self):
        return toNumPyArray(self.event.telescopeID)

    def get_event_number(self):
        return toNumPyArray(self.event.eventNumber)

    def get_run_id(self):
        return toNumPyArray(self.header.runNumber)

    def get_central_event_gps_time(self):
        timeSec = self.event.trig.timeSec
        timeNanoSec = self.event.trig.timeNanoSec
        return timeSec, timeNanoSec

    def get_local_time(self):
        timeSec = self.event.local_time_sec
        timeNanoSec = self.event.local_time_nanosec
        return timeSec, timeNanoSec

    def get_event_type(self):
        return self.event.event_type

    def get_eventType(self):
        return self.event.eventType

    def get_num_channels(self):
        return toNumPyArray(self.event.head.numGainChannels)

    def _get_adc(self, channel, telescope_id=None):
        # Expect hi/lo -> Will append Gain at the end -> hiGain/loGain
        sel_channel = self._extract_field(self.event, "%sGain" % channel)
        return sel_channel

    def get_pixel_position(self, telescope_id=None):
        return None

    def get_number_of_pixels(self, telescope_id=None):
        return None

    def get_adc_sum(self, channel, telescope_id=None):
        sel_channel = self._get_adc(channel, telescope_id)
        integrals = sel_channel.integrals

        pixelsIndices = toNumPyArray(integrals.pixelsIndices)

        # Structured array (dict of dicts)
        properties = dict()
        for par in [
            "gains",
            "maximumTimes",
            "raiseTimes",
            "tailTimes",
            "firstSplIdx"
        ]:
            properties[par] = dict(
                zip(
                    pixelsIndices,
                    toNumPyArray(self._extract_field(par))
                    )
                )
        return properties

    def get_adc_samples(self, channel, telescope_id=None):
        sel_channel = self._get_adc(channel, telescope_id)
        waveforms = sel_channel.waveforms
        samples = toNumPyArray(waveforms.samples)
        pixels = toNumPyArray(waveforms.pixelsIndices)
        npixels = len(pixels)
        samples = samples.reshape(npixels, -1)
        properties = dict(zip(pixels, samples))

        return(properties)

    def get_adcs_samples(self, telescope_id=None):
        '''
        Get the samples for all channels

        :param telescope_id: id of the telescopeof interest
        :return: dictionnary of samples (value) per pixel indices (key)
        '''
        waveforms = self.event.hiGain.waveforms
        samples = toNumPyArray(waveforms.samples)
        pixels = toNumPyArray(waveforms.pixelsIndices)
        npixels = len(pixels)
        samples = samples.reshape(npixels, -1)
        properties = dict(zip(pixels, samples))
        return(properties)

    def get_trigger_input_traces(self, telescope_id=None):
        '''
        Get the samples for all channels

        :param telescope_id: id of the telescopeof interest
        :return: dictionnary of samples (value) per pixel indices (key)
        '''
        patch_traces = toNumPyArray(self.event.trigger_input_traces)
        patches = np.arange(0, 192, 1)
        patch_traces = patch_traces.reshape(patches.shape[0], -1)
        properties = dict(zip(patches, patch_traces))

        return(properties)

    def get_trigger_output_patch7(self, telescope_id=None):
        '''
        Get the samples for all channels

        :param telescope_id: id of the telescopeof interest
        :return: dictionnary of samples (value) per pixel indices (key)
        '''
        frames = toNumPyArray(self.event.trigger_output_patch7)
        n_samples = frames.shape[0] / 18 / 3
        frames = np.unpackbits(
            frames.reshape(n_samples, 3, 18, 1), axis=-1
            )[..., ::-1].reshape(n_samples, 3, 144).reshape(n_samples, 432).T
        patches = np.arange(0, 432)
        properties = dict(zip(patches, frames))
        return(properties)

    def get_trigger_output_patch19(self, telescope_id=None):
        '''
        Get the samples for all channels

        :param telescope_id: id of the telescopeof interest
        :return: dictionnary of samples (value) per pixel indices (key)
        '''
        frames = toNumPyArray(self.event.trigger_output_patch19)
        n_samples = frames.shape[0] / 18 / 3
        frames = np.unpackbits(
            frames.reshape(n_samples, 3, 18, 1), axis=-1
            )[..., ::-1].reshape(n_samples, 3, 144).reshape(n_samples, 432).T
        patches = np.arange(0, 432)
        properties = dict(zip(patches, frames))

        return(properties)

    def get_pixel_flags(self, telescope_id = None):
        '''
        Get the flag of pixels
        :param id of the telescopeof interest
        :return: dictionnary of flags (value) per pixel indices (key)
        '''
        waveforms = self.event.hiGain.waveforms
        flags = toNumPyArray(self.event.pixels_flags)
        pixels = toNumPyArray(waveforms.pixelsIndices)
        # Structured array (dict)
        properties = dict(zip(pixels, flags))
        return(properties)

    def listof_fields(self, obj):
        return [f.name for f in obj.DESCRIPTOR.fields]


def toNumPyArray(any_array):
    any_array_type_to_numpy_type = {
        1: np.int8,
        2: np.uint8,
        3: np.int16,
        4: np.uint16,
        5: np.int32,
        6: np.uint32,
        7: np.int64,
        8: np.uint64,
        9: np.float,
        10: np.double,
    }
    if any_array.type == 0:
        raise Exception("any_array has no type")
    if any_array.type == 11:
        raise Exception("I have no idea if the boolean representation of the anyarray is the same as the numpy one")

    return np.fromstring(
        any_array.data,
        any_array_type_to_numpy_type[any_array.type]
    )
