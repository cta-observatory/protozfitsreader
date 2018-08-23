from pkg_resources import resource_string
from enum import Enum
from collections import namedtuple
import numpy as np
from astropy.io import fits
import numbers

# Beware:
#     for some reason rawzfits needs to be imported before
#     GeneratedProtocolMessageType
from . import rawzfits
# If you would like to learn more about the contents of the compiled
# rawzfits extension. Please have a look into protozfits/rawzfits.pyx
from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
from .CoreMessages_pb2 import AnyArray
from .any_array_to_numpy import any_array_to_numpy


from . import L0_pb2
from . import R1_pb2
from . import R1_LSTCam_pb2
from . import R1_NectarCam_pb2
from . import R1_DigiCam_pb2

__version__ = resource_string('protozfits', 'VERSION').decode().strip()

__all__ = [
    'File',
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


def get_class_from_PBFHEAD(pbfhead):
    module_name, class_name = pbfhead.split('.')
    return getattr(pb2_modules[module_name], class_name)


class File:

    def __init__(self, path, pure_protobuf=False):
        bintable_descriptions = detect_bintables(path)
        for btd in bintable_descriptions:
            self.__dict__[btd.extname] = Table(btd, pure_protobuf)

    def __repr__(self):
        return "%s(%r)" % (
            self.__class__.__name__,
            self.__dict__
        )

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def close(self):
        pass

    def __del__(self):
        self.close()


BinTableDescription = namedtuple(
    'BinTableDescription',
    [
        'path',
        'index',
        'extname',
        'pbfhead',
        'znaxis2',
        'header',
    ]
)


def detect_bintables(path):
    fitsfile = fits.open(path)
    bintables = [
        BinTableDescription(
            path=path,
            index=hdu_id,
            extname=hdu.header['EXTNAME'],
            pbfhead=hdu.header['PBFHEAD'],
            znaxis2=hdu.header['ZNAXIS2'],
            header=hdu.header
        )
        for hdu_id, hdu in enumerate(fitsfile)
        if 'XTENSION' in hdu.header and hdu.header['XTENSION'] == 'BINTABLE'
    ]
    fitsfile.close()
    return bintables


class Table:
    '''Iterable Table
    '''

    def __init__(self, desc, pure_protobuf=False):
        '''
        desc: BinTableDescription
        '''
        self.__desc = desc
        self.protobuf_i_fits = rawzfits.ProtobufIFits(
            self.__desc.path,
            self.__desc.extname
        )
        self.__pbuf_class = get_class_from_PBFHEAD(desc.pbfhead)
        self.header = self.__desc.header
        self.pure_protobuf = pure_protobuf

    def __len__(self):
        return self.__desc.znaxis2

    def __iter__(self):
        self.protobuf_i_fits.rewind()
        return self

    def __next__(self):
        row = self.__pbuf_class()
        row.ParseFromString(self.protobuf_i_fits.read_event())
        return self.convert(row)

    def convert(self, row):
        if not self.pure_protobuf:
            return make_namedtuple(row)
        else:
            return row

    def __repr__(self):
        return '{cn}({d.znaxis2}x{d.pbfhead})'.format(
            cn=self.__class__.__name__,
            d=self.__desc
        )

    def __getitem__(self, item):
        # getitem can get numbers, slices or iterables of numbers
        if isinstance(item, numbers.Integral):
            return self.__read_a_given_event(item)
        elif isinstance(item, slice):
            def inner():
                for event_id in range(
                    item.start or 0,
                    item.stop or len(self),
                    item.step or 1
                ):
                    yield self.__read_a_given_event(event_id)
            return inner()
        else:
            # I assume we got a iterable of event_ids
            def inner():
                for event_id in item:
                    yield self.__read_a_given_event(event_id)
            return inner()

    def __read_a_given_event(self, index):
        ''' return a given event id
        id starting at 0 not at 1
        '''
        row = self.__pbuf_class()
        row.ParseFromString(
            # counting starts at one, so we add 1
            self.protobuf_i_fits.read_a_given_event(index + 1)
        )
        return self.convert(row)


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


class MultiZFitsFiles:
    '''
    In LST they have multiple file writers, which save the incoming events
    into different files, so in case one has 10 events and 4 files,
    it might look like this:

        f1 = [0, 4]
        f2 = [1, 5, 8]
        f3 = [2, 6, 9]
        f4 = [3, 7]

    The task of MultiZFitsFiles is to open these 4 files simultaneously
    and return the events in the correct order, so the user does not really
    have to know about these existence of 4 files.
    '''

    def __init__(self, paths):
        self._files = {}
        self._events = {}

        for path in paths:
            self._files[path] = File(path).Events
            try:
                self._events[path] = next(self._files[path])
            except StopIteration:
                pass

    def __len__(self):
        total_length = sum([len(table) for table in self._events])
        return total_length

    def __iter__(self):
        return self

    def __next__(self):
        return self.next_event()

    def next_event(self):
        # check for the minimal event id
        min_path = min(
            self._events.items(),
            key=lambda item: item[1].event_id,
            default=None
        )[0]
        if min_path is None:
            raise StopIteration

        # return the minimal event id
        to_return = self._events[min_path]
        try:
            self._events[min_path] = next(self._files[min_path])
        except StopIteration:
            del self._events[min_path]

        return to_return

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        del self._files
