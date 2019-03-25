# protozmq

# Install:

    pip install git+https://github.com/cta-sst-1m/protozmq
    
The protocol buffers and zeromq are needed. With Anaconda, installing them is as simple as:

	conda install protobuf
	conda install zeromq

# Trying this out:

To use it, one must obviously start an event source, e.g.

    Build.MacOS/bin/DummyCameraServer --streams 1 --baseport 1234 --hertz 1

and then within python:

```python
from protozmq import EventSource
source = EventSource("tcp://localhost:1234")
message = source.receive_message()
```

and keep calling `receive_message()` to get the data from the real-time streams. 

With the above script, no event is forwarded downstream (see below).

# Tying it with events forwarding

The protozmq module can forward events downstream, e.g. so that they are written to disk. To try out this feature, one must start an events source, but also a zfitswriter (or message pit).

Let's work with LST events this time, and deliver only 100 events (Obviously, filenames and paths should be adapted to your setup).

    Build.Release/bin/DummyCameraServer --streams 1 --baseport 1234 --hertz 10 --totalevts 100 --input /path_to_my_file/streamer1_20180427_001.fits.fz --events_type R1
    
Now the zfitswriter:

	Build.Release/bin/ZFitsWriter --output_dir /my_directory/output --input tcp://localhost:1235 --events_type R1
	
Eventually, run the following script in python:

```python
from protozmq import EventSource
source = EventSource("tcp://localhost:1234", "tcp://*:1235")
message = "a message"
while True:
    message = source.receive_message()
    if message == "":
        break
    print("Message ID: "+str(message.event_id))

print("Got an unknown message type: stopped the loop")
```

All programs will end once the last event has been delivered. To keep the zfitswriter running, one should use the --loop command-line option.

