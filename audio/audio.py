import wave
import threading
from time import sleep
import pyaudio
import numpy as np
#import eyeD3
import sys

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)

while data != '':
    #stream.write(data)
    data = wf.readframes(CHUNK)
    eq_data = np.fromstring(data,dtype=np.int16)
    peak=np.average(np.abs(eq_data))*2
    bars="#"*int(50*peak/2**16)
    print("%05d %s"%(peak,bars))

stream.stop_stream()
stream.close()

p.terminate()
