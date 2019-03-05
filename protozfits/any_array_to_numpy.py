import numpy as np
from .CoreMessages_pb2 import AnyArray

ANY_ARRAY_TYPE_TO_NUMPY_TYPE = {
    1: np.int8,
    2: np.uint8,
    3: np.int16,
    4: np.uint16,
    5: np.int32,
    6: np.uint32,
    7: np.int64,
    8: np.uint64,
    9: np.float32,
    10: np.float64,
}

NUMPY_TYPE_TO_ANY_ARRAY_TYPE = {
    v: k for k, v in ANY_ARRAY_TYPE_TO_NUMPY_TYPE.items()
}


def any_array_to_numpy(any_array):
    if any_array.type == 0:
        if any_array.data:
            raise Exception("any_array has no type", any_array)
        else:
            return np.array([])
    if any_array.type == 11:
        print(any_array)
        raise Exception(
            "I have no idea if the boolean representation of"
            " the anyarray is the same as the numpy one",
            any_array
        )

    return np.frombuffer(
        any_array.data,
        ANY_ARRAY_TYPE_TO_NUMPY_TYPE[any_array.type]
    )


def numpy_to_any_array(np_array):
    '''convert a simple 1d numpy array into an AnyArray'''
    any_array = AnyArray()
    any_array.type = NUMPY_TYPE_TO_ANY_ARRAY_TYPE[np_array.dtype.type]
    any_array.data = np_array.tobytes()
    return any_array


def assign_numpy_array_to_pbuf(np_array, pbuf):
    pbuf.type = NUMPY_TYPE_TO_ANY_ARRAY_TYPE[np_array.dtype.type]
    pbuf.data = np_array.tobytes()
