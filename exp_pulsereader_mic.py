import wave
import pyaudio
import struct
import obj_pulseread




pulse_size = 0.0055





CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 100
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

import obj_pulseread

datar = obj_pulseread.read_pulse(RATE, pulse_size)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	for x in range(CHUNK):
		data = stream.read(1)
		value = struct.unpack('h', data)[0]
		datar.frame(value)