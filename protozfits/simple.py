from enum import Enum
from collections import namedtuple
from astropy.io import fits

from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
from . import rawzfitsreader
from . import L0_pb2
from .CoreMessages_pb2 import AnyArray
from .any_array_to_numpy import any_array_to_numpy


class File:
    def __init__(self, path):
        bintable_descriptions = detect_bintables(path)
        for btd in bintable_descriptions:
            self.__dict__[btd.extname] = Table(btd)

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
        'pb_class_name',
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
            pb_class_name=hdu.header['PBFHEAD'].split('.')[-1],
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

    def __init__(self, desc):
        '''
        desc: BinTableDescription
        '''
        self.__desc = desc
        self.__pbuf_class = getattr(L0_pb2, desc.pb_class_name)
        self.header = self.__desc.header

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
            return make_namedtuple(row)
        except EOFError:
            raise StopIteration

    def __repr__(self):
        return '{cn}({d.extname}: {d.znaxis2}x{d.pb_class_name})'.format(
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


messages = set([
    getattr(L0_pb2, name)
    for name in dir(L0_pb2)
    if isinstance(getattr(L0_pb2, name), GeneratedProtocolMessageType)
])

named_tuples = {
    m: namedtuple(
        m.__name__,
        list(m.DESCRIPTOR.fields_by_name)
    )
    for m in messages
}

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


def rewind_table():
    # rawzfitsreader.rewindTable() has a bug at the moment,
    # it always throws a SystemError
    # we let that one pass
    try:
        rawzfitsreader.rewindTable()
    except SystemError:
        pass
