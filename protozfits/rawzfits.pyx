# distutils: language = c++
import numpy as np
cimport numpy as np
from libcpp.string cimport string
from libcpp cimport bool as bool_t
from libcpp.vector cimport vector
from collections import namedtuple


cdef extern from "ProtobufIFits.h" namespace "ACTL::IO":
    cdef cppclass _ProtobufIFits "ACTL::IO::ProtobufIFits":
        _ProtobufIFits(
            const string fname,
            const string tableName
        ) except +

        void CheckIfFileIsConsistent(bool_t update_catalog) except +

        int getNumMessagesInTable()
        string readSerializedMessage(int number)


cdef extern from "ProtoSerialZOFits.h" namespace "ACTL::IO":
    cdef cppclass _ProtoSerialZOFits "ACTL::IO::ProtoSerialZOFits":
        _ProtoSerialZOFits() except +
        void open(const char* filename) except +
        bool_t close() except +
        void moveToNewTable(string tablename, string message_name) except +
        void writeSerializedMessage(string& serializedMessage) except +


cdef class ProtobufIFits:
    cdef _ProtobufIFits* c_protobufifits
    cdef int n_events
    cdef string exchange_string

    def __cinit__(self, fname, tablename=""):
        self.c_protobufifits = new _ProtobufIFits(
            bytes(fname, 'ascii'),
            bytes(tablename, 'ascii')
        )
        self.n_events = 0
        self.exchange_string = ""

    def __dealloc__(self):
        del self.c_protobufifits

    def CheckIfFileIsConsistent(self, update_catalog):
        self.c_protobufifits.CheckIfFileIsConsistent(update_catalog)

    def read_event(self):
        self.n_events += 1
        if self.c_protobufifits.getNumMessagesInTable() < self.n_events:
            raise StopIteration
        return self.c_protobufifits.readSerializedMessage(self.n_events)

    def read_a_given_event(self, event_id):
        tmp = self.n_events
        try:
            self.n_events = event_id - 1
            return self.read_event()
        except:
            self.n_events = tmp
            raise

    def num_rows(self):
        return self.c_protobufifits.getNumMessagesInTable()

    def rewind(self):
        self.n_events = 0


cdef class ProtoSerialZOFits:
    cdef _ProtoSerialZOFits* c_proto_serial_zofits

    def __cinit__(self, fname):
        self.c_proto_serial_zofits = new _ProtoSerialZOFits()
        self.c_proto_serial_zofits.open(bytes(fname, 'ascii'))

    def __dealloc__(self):
        self.close()
        del self.c_proto_serial_zofits

    def close(self):
        return self.c_proto_serial_zofits.close()

    def move_to_new_table(self, tablename, message_name):
        self.c_proto_serial_zofits.moveToNewTable(
            bytes(tablename, 'ascii'),
            bytes(message_name, 'ascii')
        )

    def write_serialized_message(self, msg):
        self.c_proto_serial_zofits.writeSerializedMessage(msg)
