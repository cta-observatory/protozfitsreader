# Protozfits [![Build Status](https://travis-ci.org/cta-sst-1m/protozfitsreader.svg?branch=master)](https://travis-ci.org/cta-sst-1m/protozfitsreader)



If you are just starting with proto-z-fits files and would like to explore the file contents, try this:

### Open a file
```
>>> from protozfits import File
>>> example_path = 'protozfits/tests/resources/example_9evts_NectarCAM.fits.fz'
>>> file = File(example_path)
>>> file
File({
    'RunHeader': Table(1xDataModel.CameraRunHeader),
    'Events': Table(9xDataModel.CameraEvent)
})
```

From this we learn, the `file` contains two `Table` named `RunHeader` and `Events` which
contains 9 rows of type `CameraEvent`. There might be more tables with
other types of rows in other files. For instance LST has its `RunHeader` called `CameraConfig`.

### Getting an event

Usually people just iterate over a whole `Table` like this:
```python
for event in file.Events:
    # do something with the event
    pass
```

But if you happen to know exactly which event you want, you can also
directly get an event, like this:
```python
event_17 = file.Events[17]
```

You can also get a range of events, like this:
```python
for event in file.Events[100:200]:
    # do something events 100 until 200
    pass
```

It is not yet possible to specify negative indices, like `file.Events[:-10]`
does *not work*.

If you happen to have a list or any iterable or a generator with event ids
you are interested in you can get the events in question like this:

```python
interesting_event_ids = range(100, 200, 3)
for event in file.Events[interesting_event_ids]:
    # do something with intesting events
    pass
```

### RunHeader

Even though there is usually **only one** run header per file, technically
this single run header is stored in a Table. This table could contain multiple
"rows" and to me it is not clear what this would mean... but technically it is
possible.

At the moment I would recommend getting the run header out of the file
we opened above like this (replace RunHeader with CameraConfig for LST data):

```python
assert len(file.RunHeader) == 1
header = file.RunHeader[0]
```


For now, I will just get the next event
```python
event = file.Events[0]
type(event)
<class 'protozfits.CameraEvent'>
event._fields
('telescopeID', 'dateMJD', 'eventType', 'eventNumber', 'arrayEvtNum', 'hiGain', 'loGain', 'trig', 'head', 'muon', 'geometry', 'hilo_offset', 'hilo_scale', 'cameraCounters', 'moduleStatus', 'pixelPresence', 'acquisitionMode', 'uctsDataPresence', 'uctsData', 'tibDataPresence', 'tibData', 'swatDataPresence', 'swatData', 'chipsFlags', 'firstCapacitorIds', 'drsTagsHiGain', 'drsTagsLoGain', 'local_time_nanosec', 'local_time_sec', 'pixels_flags', 'trigger_map', 'event_type', 'trigger_input_traces', 'trigger_output_patch7', 'trigger_output_patch19', 'trigger_output_muon', 'gps_status', 'time_utc', 'time_ns', 'time_s', 'flags', 'ssc', 'pkt_len', 'muon_tag', 'trpdm', 'pdmdt', 'pdmt', 'daqtime', 'ptm', 'trpxlid', 'pdmdac', 'pdmpc', 'pdmhi', 'pdmlo', 'daqmode', 'varsamp', 'pdmsum', 'pdmsumsq', 'pulser', 'ftimeoffset', 'ftimestamp', 'num_gains')
event.hiGain.waveforms.samples
array([241, 245, 248, ..., 218, 214, 215], dtype=int16)
```

An LST event will look something like so:
```python
>>> event
CameraEvent(
    configuration_id=1
    event_id=1
    tel_event_id=1
    trigger_time_s=0
    trigger_time_qns=0
    trigger_type=0
    waveform=array([  0,   0, ..., 288, 263], dtype=uint16)
    pixel_status=array([ 0,  0,  0,  0,  0,  0,  0, 12, 12, 12, 12, 12, 12, 12], dtype=uint8)
    ped_id=0
    nectarcam=NectarCamEvent(
        module_status=array([], dtype=float64)
        extdevices_presence=0
        tib_data=array([], dtype=float64)
        cdts_data=array([], dtype=float64)
        swat_data=array([], dtype=float64)
        counters=array([], dtype=float64))
    lstcam=LstCamEvent(
        module_status=array([0, 1], dtype=uint8)
        extdevices_presence=0
        tib_data=array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=uint8)
        cdts_data=array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0], dtype=uint8)
        swat_data=array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0], dtype=uint8)
        counters=array([  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                 0,   0,   1,   0,   0,   0,  31,   0,   0,   0, 243, 170, 204,
                 0,   0,   0,   0,   0], dtype=uint8)
        chips_flags=array([    0,     0,     0,     0,     0,     0,     0,     0, 61440,
                 245, 61440,   250, 61440,   253, 61440,   249], dtype=uint16)
        first_capacitor_id=array([    0,     0,     0,     0,     0,     0,     0,     0, 61440,
                 251, 61440,   251, 61440,   241, 61440,   245], dtype=uint16)
        drs_tag_status=array([ 0, 12], dtype=uint8)
        drs_tag=array([   0,    0, ..., 2021, 2360], dtype=uint16))
    digicam=DigiCamEvent(
        ))
>>> event.waveform
array([  0,   0,   0, ..., 292, 288, 263], dtype=uint16)
```

`event` supports tab-completion, which I regard as very important while exploring.
It is implemented using [`collections.namedtuple`](https://docs.python.org/3.6/library/collections.html#collections.namedtuple).
I tried to create a useful string represenation, it is very long, yes ... but I
hope you can still enjoy it:
```python
>>> event
CameraEvent(
    telescopeID=1
    dateMJD=0.0
    eventType=<eventType.NONE: 0>
    eventNumber=97750287
    arrayEvtNum=0
    hiGain=PixelsChannel(
        waveforms=WaveFormData(
            samples=array([241, 245, ..., 214, 215], dtype=int16)
            pixelsIndices=array([425, 461, ..., 727, 728], dtype=uint16)
            firstSplIdx=array([], dtype=float64)
            num_samples=0
            baselines=array([232, 245, ..., 279, 220], dtype=int16)
            peak_time_pos=array([], dtype=float64)
            time_over_threshold=array([], dtype=float64))
        integrals=IntegralData(
            gains=array([], dtype=float64)
            maximumTimes=array([], dtype=float64)
            tailTimes=array([], dtype=float64)
            raiseTimes=array([], dtype=float64)
            pixelsIndices=array([], dtype=float64)
            firstSplIdx=array([], dtype=float64)))
# [...]
```

### Table header

`fits.fz` files are still normal [FITS files](https://fits.gsfc.nasa.gov/) and
each Table in the file corresponds to a so called "BINTABLE" extension, which has a
header. You can access this header like this:
```
>>> file.Events
Table(100xDataModel.CameraEvent)
>>> file.Events.header
# this is just a sulection of all the contents of the header
XTENSION= 'BINTABLE'           / binary table extension
BITPIX  =                    8 / 8-bit bytes
NAXIS   =                    2 / 2-dimensional binary table
NAXIS1  =                  192 / width of table in bytes
NAXIS2  =                    1 / number of rows in table
TFIELDS =                   12 / number of fields in each row
EXTNAME = 'Events'             / name of extension table
CHECKSUM= 'BnaGDmS9BmYGBmY9'   / Checksum for the whole HDU
DATASUM = '1046602664'         / Checksum for the data block
DATE    = '2017-10-31T02:04:55' / File creation date
ORIGIN  = 'CTA'                / Institution that wrote the file
WORKPKG = 'ACTL'               / Workpackage that wrote the file
DATEEND = '1970-01-01T00:00:00' / File closing date
PBFHEAD = 'DataModel.CameraEvent' / Written message name
CREATOR = 'N4ACTL2IO14ProtobufZOFitsE' / Class that wrote this file
COMPILED= 'Oct 26 2017 16:02:50' / Compile time
TIMESYS = 'UTC'                / Time system
>>> file.Events.header['DATE']
'2017-10-31T02:04:55'
>>> type(file.Events.header)
<class 'astropy.io.fits.header.Header'>
```
The header is provided by [`astropy`](http://docs.astropy.org/en/stable/io/fits/#working-with-fits-headers).


### Multiple input files reading in parallel

Reading multiple files in parallel is possible only for the R1 datamodel, sorting incoming events by their event_id field.
For this use the MultiZFitsFiles class, still from protozfits. There is currently two syntaxes available. Either the
same one as for the iteratable File object (just iterate on a multifile object), or by directly calling the next_event() method. For instance the following code reads two files in parallel, in two different ways:
```python
>>> from protozfits import MultiZFitsFiles
>>> multi_files = MultiZFitsFiles([
        '/local/etienne/streamer1_20180427_000.fits.fz',
        '/local/etienne/streamer1_20180427_001.fits.fz'
    ])
>>> event = multi_files.next_event()
>>> event.event_id
1
>>> event = multi_files.next_event()
>>> event.event_id
2
>>> for i_evt, event in enumerate(multi_files):
>>>    print(event.event_id)
3
4
5
6
...

```

### Table Headers in case of `MultiZFitsFiles`

You can access the Table Headers of the "Events" Tables when using `MultiZFitsFiles`.
`headers` is a dict-of-dicts, the first key is the original FITS key
and only the second key is the file path.
So if you would like to check e.g. the "PBFHEAD" of all used files you can do this:
```python
from protozfits import MultiZFitsFiles
from glob import glob

multi_files = MultiZFitsFiles(glob('Run0027.*.fits.fz'))
print(multi_files.headers['PBFHEAD'])
# Result:
# {'Run0027.0003.fits.fz': 'R1.CameraEvent',
#  'Run0027.0000.fits.fz': 'R1.CameraEvent',
#  'Run0027.0001.fits.fz': 'R1.CameraEvent',
#  'Run0027.0002.fits.fz': 'R1.CameraEvent'}

# or
assert all(v=='R1.CameraEvent' for v in multi_files.headers['PBFHEAD'].values())
```

### Isn't this a little slow?

Well, indeed, converting the original google protobuf instances into namedtuples full of
"useful" Python values takes time. And in case you for example know exactly what you want
from the file, then you can get a speed up doing it like this:
```
>>> from protozfits import File
>>> file = File(example_path, pure_protobuf=True)
>>> event = next(file.Events)
>>> type(event)
<class 'L0_pb2.CameraEvent'>
```

Now iterating over the file is much faster then before. But you have no
tab-completion and some contents are useless for you, but some are just fine:
```
>>> event.eventNumber
97750288   # <--- just fine
>>> event.hiGain.waveforms.samples

type: S16
data: "\362\000\355\000 ... "   # <---- goes on "forever" .. utterly useless
>>> type(event.hiGain.waveforms.samples)
<class 'CoreMessages_pb2.AnyArray'>
```
You can convert these `AnyArray`s into numpy arrays like this:
```
>>> from protozfits import any_array_to_numpy
>>> any_array_to_numpy(event.hiGain.waveforms.samples)
array([242, 237, 234, ..., 218, 225, 229], dtype=int16)
```

So ... I hope based on this little example you can implement your own reader,
which is optimized for your telescope.

If you have questions, please open an issue or a pull request to improve this documentation.


## Installation:

We all use [Anaconda](https://www.anaconda.com/) and this package is tested
against Anaconda. You can [download anaconda](https://www.anaconda.com/download) for your system for free.

You do not have to use a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html) to use this package. It cleanly installs and uninstalls with [pip](https://docs.python.org/3.6/installing/). If you plan to play around with different versions of this package your might want to use environments though.

### Linux / OSX (with anaconda)

    pip install https://github.com/cta-sst-1m/protozfitsreader/archive/v1.4.0.tar.gz

### Most common issues and possible remedies

- Cannot import `_message`, message along the lines of:
```
    from google.protobuf.pyext import _message
    ImportError: cannot import name _message
```
Try uninstalling conda-protobuf and reinstalling from pypi, like this:

    conda uninstall protobuf --yes
    pip install protobuf
    
### Miniconda & Faster installation?

If you use **Ana**conda this is not interesting for you, but if you use **Mini**conda,
then please read on.

You could just `pip install` this and it would use `pip` to install all the dependencies.
But `pip install <some package>` is sometimes much slower than `conda install <some package>`.

Two of the requirements of this package are `numpy` and `protobuf`.
We think installing them with `pip` is very slow, so we recommend to

    conda install numpy astropy

before `pip`-installing this package for your convenience.

### To developers: No `pip --editable`

This package contains pre-build binaries, which (at the moment) are required to be installed
into your "site-packages" folder.
Developers like to install packages they are currently developing like this:

    pip install --editable .

Because then they can modify code and try it out without constant uninstall/install cycles.
Unfortunately this nice development workcycle is not possible at the moment.

I personally do:

    git clone https://github.com/cta-sst-1m/protozfitsreader
    pip install protozfits
    # play around ... modify ...
    pip uninstall protozfits --yes && pip install protozfits
    # play around ... modify ...
    pip uninstall protozfits --yes && pip install protozfits
    # and so on

The uninstall/install takes 1..2sec ... so it is rather ok... not perfect though.


## Where does this come from?

The contents of this repo are based tar-balls thankfully generated by E. Lyard.
The [difference is explained](patching_so_files.md) on a seprate page.
