from enum import Enum
from collections import namedtuple
import numpy as np
from astropy.io import fits

from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
from . import rawzfitsreader
from .CoreMessages_pb2 import AnyArray
from .any_array_to_numpy import any_array_to_numpy


from . import L0_pb2
from . import R1_pb2

pb2_modules = {
    'R1': R1_pb2,
    'L0': L0_pb2,
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
    __last_opened = None
    '''the rawzfitsreader has a "bug" which is: It cannot have two open
    hdus. So when the File would open all N tables at construction time,
    every `rawzfitsreader.readEvent()` would act on the last opened table.

    So the Tables remember which hdu was opened last, and if it was not them.
    They open it.
    '''

    def __init__(self, desc, pure_protobuf=False):
        '''
        desc: BinTableDescription
        '''
        self.__desc = desc
        self.__pbuf_class = get_class_from_PBFHEAD(desc.pbfhead)
        self.header = self.__desc.header
        self.pure_protobuf = pure_protobuf

    def __len__(self):
        return self.__desc.znaxis2

    def __iter__(self):
        rewind_table()
        return self

    def __next__(self):
        if not Table.__last_opened == self.__desc:
            rawzfitsreader.open(self.__desc.path+":"+self.__desc.extname)
            Table.__last_opened = self.__desc
        row = self.__pbuf_class()
        try:
            row.ParseFromString(rawzfitsreader.readEvent())
            if not self.pure_protobuf:
                return make_namedtuple(row)
            else:
                return row
        except EOFError:
            raise StopIteration

    def __repr__(self):
        return '{cn}({d.znaxis2}x{d.pbfhead})'.format(
            cn=self.__class__.__name__,
            d=self.__desc
        )


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


def collect_messages_from_pb2_modules(pb2_modules):
    messages = set()
    for module in pb2_modules.values():
        for name in dir(module):
            thing = getattr(module, name)
            if isinstance(thing, GeneratedProtocolMessageType):
                messages.add(thing)


def create_named_tuple_from_message(message):
    _nt = namedtuple(
        message.__name__,
        list(message.DESCRIPTOR.fields_by_name)
    )

    def namedtuple_repr(self):
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

    _nt.__repr__ = namedtuple_repr
    return _nt




def rewind_table():
    # rawzfitsreader.rewindTable() has a bug at the moment,
    # it always throws a SystemError
    # we let that one pass
    try:
        rawzfitsreader.rewindTable()
    except SystemError:
        pass



def collect_namedtuples():
    messages = collect_messages_from_pb2_modules()
    return make_namedtuples_from_messages(messages)


def make_namedtuples_from_messages(messages):
    named_tuples = {m: nt(m) for m in messages}
    return named_tuples


def make_enum_types_from_messages(messages):
    enum_types = {}
    for m in messages:
        enum = make_enum_from_message(m)
        enum_types[(m, enum.__name__)] = enum


def make_enum_from_message(m):
    d = m.DESCRIPTOR
    for field in d.fields:
        if field.enum_type is not None:
            et = field.enum_type
            return Enum(
                field.name,
                zip(et.values_by_name, et.values_by_number)
            )
