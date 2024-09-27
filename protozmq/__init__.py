from pkg_resources import resource_string
from enum import Enum
from collections import namedtuple
import numpy as np

from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
from protozfits.CoreMessages_pb2 import AnyArray
from protozfits.any_array_to_numpy import any_array_to_numpy

import zmq

from protozfits import CoreMessages_pb2
from protozfits import L0_pb2
from protozfits import R1_pb2
from protozfits import R1_LSTCam_pb2
from protozfits import R1_NectarCam_pb2
from protozfits import R1_DigiCam_pb2

__version__ = resource_string('protozmq', 'VERSION').decode().strip()


__all__ = [
    'EventSource',
    'make_namedtuple',
    'any_array_to_numpy',
]

pb2_modules = {
    'L0': L0_pb2,
    'DataModel': L0_pb2,
    'R1': R1_pb2,
    'R1_DigiCam': R1_DigiCam_pb2,
    'R1_NectarCam': R1_NectarCam_pb2,
    'R1_LSTCam': R1_LSTCam_pb2,
}


class EventSource:

    context = zmq.Context()
    in_socket  = context.socket(zmq.PULL)
    out_socket = context.socket(zmq.PUSH)
    cta_message = CoreMessages_pb2.CTAMessage()
    L0_message = L0_pb2.CameraEvent()
    R1_message = R1_pb2.CameraEvent()
    forward_messages = False

    def __init__(self, zmq_in_config, zmq_out_config=""):
        '''
        data_type can be set to the string "R1" in order to read
        R1_pb2.CameraEvents, by default this reads L0_pb2.CameraEvents.
        '''
        self.in_socket.connect(zmq_in_config)
        if zmq_out_config != "":
            self.forward_messages = True
            self.out_socket.bind(zmq_out_config)

    def receive_message(self):
        binary_message = self.in_socket.recv()
        if self.forward_messages == True:
            self.out_socket.send(binary_message)

        self.cta_message.ParseFromString(binary_message)

        if self.cta_message.payload_type[0] == 16:
            self.R1_message.ParseFromString(self.cta_message.payload_data[0])
            return make_namedtuple(self.R1_message)

        if self.cta_message.payload_type[0] == 8:
            self.L0_message.ParseFromString(self.cta_message.payload_data[0])
            return make_namedtuple(self.L0_message)

        print("Message type " + str(self.cta_message.payload_type[0]) + " not handled yet")

        return ""

# Everything below is strictly identical to what is in protozfits.__init__
# Will be moved into its own package soon.


def make_namedtuple(message):
    namedtuple_class = named_tuples[message.__class__]
    return namedtuple_class._make(
        message_getitem(message, name)
        for name in namedtuple_class._fields
    )


def message_getitem(msg, name):
    value = msg.__getattribute__(name)
    if isinstance(value, AnyArray):
        value = any_array_to_numpy(value)
    elif (msg.__class__, name) in enum_types:
        value = enum_types[(msg.__class__, name)](value)
    elif type(value) in named_tuples:
        value = make_namedtuple(value)
    return value

messages = set()
for module in pb2_modules.values():
    for name in dir(module):
        thing = getattr(module, name)
        if isinstance(thing, GeneratedProtocolMessageType):
            messages.add(thing)


def namedtuple_repr2(self):
    '''a nicer repr for big namedtuples containing big numpy arrays'''
    old_print_options = np.get_printoptions()
    np.set_printoptions(precision=3, threshold=50, edgeitems=2)
    delim = '\n    '
    s = self.__class__.__name__ + '(' + delim

    s += delim.join([
        '{0}={1}'.format(
            key,
            repr(
                getattr(self, key)
            ).replace('\n', delim)
        )
        for key in self._fields
    ])
    s += ')'
    np.set_printoptions(**old_print_options)
    return s


def nt(m):
    '''create namedtuple class from protobuf.message type'''
    _nt = namedtuple(
        m.__name__,
        list(m.DESCRIPTOR.fields_by_name)
    )
    _nt.__repr__ = namedtuple_repr2
    return _nt

named_tuples = {m: nt(m) for m in messages}

enum_types = {}
for m in messages:
    d = m.DESCRIPTOR
    for field in d.fields:
        if field.enum_type is not None:
            et = field.enum_type
            enum = Enum(
                field.name,
                zip(et.values_by_name, et.values_by_number)
            )
            enum_types[(m, field.name)] = enum


