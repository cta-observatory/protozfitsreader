from pkg_resources import resource_string
from enum import Enum
from collections import namedtuple
from warnings import warn
import numpy as np
from astropy.io import fits

# Beware:
#     for some reason rawzfitsreader needs to be imported before
#     GeneratedProtocolMessageType
from . import rawzfitsreader
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
    'any_array_to_numpy',
]

pb2_modules = [
    L0_pb2,
    R1_pb2,
    R1_DigiCam_pb2,
    R1_NectarCam_pb2,
    R1_LSTCam_pb2,
]

klasses = {}


def make_convert_any_array(fd):
    def convert_any_array(self):
        return any_array_to_numpy(getattr(self._message, fd.name))
    return convert_any_array


def make_wrap_in_class(fd):
    def wrap_in_class(self):
        klass = klasses[fd.message_type.full_name]
        return klass(getattr(self._message, fd.name))
    return wrap_in_class


def make_return_normal_field(fd):
    def return_normal_field(self):
        return getattr(self._message, fd.name)
    return return_normal_field


def make__repr__(msg):
    fields = [n for n in msg.DESCRIPTOR.fields_by_name]

    def nice_repr(self):
        '''a nicer repr for messages containing big numpy arrays'''
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
            for key in fields
        ])
        s += ')'
        np.set_printoptions(**old_print_options)
        return s

    return nice_repr


def message_to_class(msg):
    d = msg.DESCRIPTOR
    fields = {}

    def __init__(self, message):
        self._message = message
    fields['__init__'] = __init__
    fields['DESCRIPTOR'] = d
    fields['__repr__'] = make__repr__(msg)

    for fd in d.fields:
        if fd.message_type is not None:
            if fd.message_type.name == 'AnyArray':
                fields[fd.name] = property(fget=make_convert_any_array(fd))
            else:
                fields[fd.name] = property(fget=make_wrap_in_class(fd))
        else:
            fields[fd.name] = property(fget=make_return_normal_field(fd))

    return type(d.full_name, (object, ), fields)

for module in pb2_modules:
    for name in dir(module):
        thing = getattr(module, name)
        if isinstance(thing, GeneratedProtocolMessageType):
            klasses[thing.DESCRIPTOR.full_name] = message_to_class(thing)


def get_class_from_PBFHEAD(pbfhead):
    package, msg_name = pbfhead.split('.')
    for module in pb2_modules:
        if module.DESCRIPTOR.package == package:
            try:
                return getattr(module, msg_name)
            except Exception as e:
                print(e)
    raise KeyError('Could not find {} in package: {}'.format(
        msg_name, package)
    )


class File:
    instances = 0

    def __init__(self, path):
        File.instances += 1
        if File.instances > 1:
            warn('''\
        Multiple open zfits files at the same time are not supported.
        Reading from mutliple open tables at the same time will reset these
        tables continously and you will read always the same events.
        ''')
        Table._Table__last_opened = None
        bintable_descriptions = detect_bintables(path)
        for btd in bintable_descriptions:
            self.__dict__[btd.extname] = Table(btd)

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
        File.instances -= 1

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
        self.__pbuf_class = get_class_from_PBFHEAD(desc.pbfhead)
        self.__klass = klasses[desc.pbfhead]
        self.header = self.__desc.header

    def __len__(self):
        return self.__desc.znaxis2

    def __iter__(self):
        return self

    def __next__(self):
        if not Table.__last_opened == self.__desc:
            rawzfitsreader.open(self.__desc.path+":"+self.__desc.extname)
            Table.__last_opened = self.__desc
        row = self.__pbuf_class()
        try:
            row.ParseFromString(rawzfitsreader.readEvent())
            return self.__klass(row)
        except EOFError:
            raise StopIteration

    def __repr__(self):
        return '{cn}({d.znaxis2}x{d.pbfhead})'.format(
            cn=self.__class__.__name__,
            d=self.__desc
        )


messages = []
for module in pb2_modules:
    for name in dir(module):
        thing = getattr(module, name)
        if isinstance(thing, GeneratedProtocolMessageType):
            messages.append(thing)


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
