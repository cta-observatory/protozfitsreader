from os.path import isfile
import numpy as np
from . import rawzfitsreader
from . import L0_pb2
import warnings

PATCH_ID_INPUT = [
    204, 216, 180, 192, 229, 241, 205, 217, 254, 266, 230, 242,
    279, 291, 255, 267, 304, 316, 280, 292, 329, 341, 305, 317, 156, 168, 132,
    144, 181, 193, 157, 169, 206, 218, 182, 194, 231, 243, 207, 219, 256, 268,
    232, 244, 281, 293, 257, 269, 108, 120, 84, 96, 133, 145, 109, 121, 158,
    170, 134, 146, 183, 195, 159, 171, 208, 220, 184, 196, 233, 245, 209, 221,
    60, 72, 40, 50, 85, 97, 61, 73, 110, 122, 86, 98, 135, 147, 111, 123, 160,
    172, 136, 148, 185, 197, 161, 173, 24, 32, 12, 18, 41, 51, 25, 33, 62, 74,
    42, 52, 87, 99, 63, 75, 112, 124, 88, 100, 137, 149, 113, 125, 4, 8, 0, 2,
    13, 19, 5, 9, 26, 34, 14, 20, 43, 53, 27, 35, 64, 76, 44, 54, 89, 101, 65,
    77, 228, 239, 240, 252, 251, 262, 263, 275, 274, 285, 286, 298, 297, 308,
    309, 321, 320, 331, 332, 344, 343, 354, 355, 366, 253, 264, 265, 277, 276,
    287, 288, 300, 299, 310, 311, 323, 322, 333, 334, 346, 345, 356, 357, 368,
    367, 377, 378, 387, 278, 289, 290, 302, 301, 312, 313, 325, 324, 335, 336,
    348, 347, 358, 359, 370, 369, 379, 380, 389, 388, 396, 397, 404, 303, 314,
    315, 327, 326, 337, 338, 350, 349, 360, 361, 372, 371, 381, 382, 391, 390,
    398, 399, 406, 405, 411, 412, 417, 328, 339, 340, 352, 351, 362, 363, 374,
    373, 383, 384, 393, 392, 400, 401, 408, 407, 413, 414, 419, 418, 422, 423,
    426, 353, 364, 365, 376, 375, 385, 386, 395, 394, 402, 403, 410, 409, 415,
    416, 421, 420, 424, 425, 428, 427, 429, 430, 431, 215, 191, 227, 203, 167,
    143, 179, 155, 119, 95, 131, 107, 71, 49, 83, 59, 31, 17, 39, 23, 7, 1,
    11, 3, 238, 214, 250, 226, 190, 166, 202, 178, 142, 118, 154, 130, 94, 70,
    106, 82, 48, 30, 58, 38, 16, 6, 22, 10, 261, 237, 273, 249, 213, 189, 225,
    201, 165, 141, 177, 153, 117, 93, 129, 105, 69, 47, 81, 57, 29, 15, 37,
    21, 284, 260, 296, 272, 236, 212, 248, 224, 188, 164, 200, 176, 140, 116,
    152, 128, 92, 68, 104, 80, 46, 28, 56, 36, 307, 283, 319, 295, 259, 235,
    271, 247, 211, 187, 223, 199, 163, 139, 175, 151, 115, 91, 127, 103, 67,
    45, 79, 55, 330, 306, 342, 318, 282, 258, 294, 270, 234, 210, 246, 222,
    186, 162, 198, 174, 138, 114, 150, 126, 90, 66, 102, 78
]

PATCH_ID_OUTPUT = [
    204, 216, 229, 241, 254, 266, 279, 291, 304, 316, 329,
    341, 180, 192, 205, 217, 230, 242, 255, 267, 280, 292, 305, 317, 156, 168,
    181, 193, 206, 218, 231, 243, 256, 268, 281, 293, 132, 144, 157, 169, 182,
    194, 207, 219, 232, 244, 257, 269, 108, 120, 133, 145, 158, 170, 183, 195,
    208, 220, 233, 245, 84, 96, 109, 121, 134, 146, 159, 171, 184, 196, 209,
    221, 60, 72, 85, 97, 110, 122, 135, 147, 160, 172, 185, 197, 40, 50, 61,
    73, 86, 98, 111, 123, 136, 148, 161, 173, 24, 32, 41, 51, 62, 74, 87, 99,
    112, 124, 137, 149, 12, 18, 25, 33, 42, 52, 63, 75, 88, 100, 113, 125, 4,
    8, 13, 19, 26, 34, 43, 53, 64, 76, 89, 101, 0, 2, 5, 9, 14, 20, 27, 35,
    44, 54, 65, 77, 228, 239, 251, 262, 274, 285, 297, 308, 320, 331, 343,
    354, 240, 252, 263, 275, 286, 298, 309, 321, 332, 344, 355, 366, 253, 264,
    276, 287, 299, 310, 322, 333, 345, 356, 367, 377, 265, 277, 288, 300, 311,
    323, 334, 346, 357, 368, 378, 387, 278, 289, 301, 312, 324, 335, 347, 358,
    369, 379, 388, 396, 290, 302, 313, 325, 336, 348, 359, 370, 380, 389, 397,
    404, 303, 314, 326, 337, 349, 360, 371, 381, 390, 398, 405, 411, 315, 327,
    338, 350, 361, 372, 382, 391, 399, 406, 412, 417, 328, 339, 351, 362, 373,
    383, 392, 400, 407, 413, 418, 422, 340, 352, 363, 374, 384, 393, 401, 408,
    414, 419, 423, 426, 353, 364, 375, 385, 394, 402, 409, 415, 420, 424, 427,
    429, 365, 376, 386, 395, 403, 410, 416, 421, 425, 428, 430, 431, 215, 191,
    167, 143, 119, 95, 71, 49, 31, 17, 7, 1, 227, 203, 179, 155, 131, 107, 83,
    59, 39, 23, 11, 3, 238, 214, 190, 166, 142, 118, 94, 70, 48, 30, 16, 6,
    250, 226, 202, 178, 154, 130, 106, 82, 58, 38, 22, 10, 261, 237, 213, 189,
    165, 141, 117, 93, 69, 47, 29, 15, 273, 249, 225, 201, 177, 153, 129, 105,
    81, 57, 37, 21, 284, 260, 236, 212, 188, 164, 140, 116, 92, 68, 46, 28,
    296, 272, 248, 224, 200, 176, 152, 128, 104, 80, 56, 36, 307, 283, 259,
    235, 211, 187, 163, 139, 115, 91, 67, 45, 319, 295, 271, 247, 223, 199,
    175, 151, 127, 103, 79, 55, 330, 306, 282, 258, 234, 210, 186, 162, 138,
    114, 90, 66, 342, 318, 294, 270, 246, 222, 198, 174, 150, 126, 102, 78
]


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

        self.pixel_ids = toNumPyArray(_w.pixelsIndices)
        self._sort_ids = np.argsort(self.pixel_ids)
        self.n_pixels = len(self.pixel_ids)
        self._samples = toNumPyArray(_w.samples).reshape(self.n_pixels, -1)
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
        self.pixel_flags = toNumPyArray(_e.pixels_flags)[self._sort_ids]
        self.adc_samples = self._samples[self._sort_ids]
        self.trigger_output_patch7 = _prepare_trigger_output(
            _e.trigger_output_patch7)
        self.trigger_output_patch19 = _prepare_trigger_output(
            _e.trigger_output_patch19)
        self.trigger_input_traces = _prepare_trigger_input(
            _e.trigger_input_traces)

    @property
    def unsorted_baseline(self):
        if not hasattr(self, '__unsorted_baseline'):
            try:
                self.__unsorted_baseline = toNumPyArray(
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


def _prepare_trigger_input(_a):
    _a = toNumPyArray(_a)
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
    _a = toNumPyArray(_a)
    A, B, C = 3, 18, 8

    _a = np.unpackbits(_a.reshape(-1, A, B, 1), axis=-1)
    _a = _a[..., ::-1]
    _a = _a.reshape(-1, A*B*C).T
    return _a[np.argsort(PATCH_ID_OUTPUT)]


any_array_type_to_npdtype = {
    1: 'i1',
    2: 'u1',
    3: 'i2',
    4: 'u2',
    5: 'i4',
    6: 'u4',
    7: 'i8',
    8: 'u8',
    9: 'f4',
    10: 'f8',
}

any_array_type_cannot_convert_exception_text = {
    0: "This any array has no defined type",
    11: """I have no idea if the boolean representation
        of the anyarray is the same as the numpy one"""
}


def toNumPyArray(a):
    if a.type in any_array_type_to_npdtype:
        return np.frombuffer(
            a.data, any_array_type_to_npdtype[a.type])
    else:
        raise ValueError(
            "Conversion to NumpyArray failed with error:\n%s",
            any_array_type_cannot_convert_exception_text[a.type])
