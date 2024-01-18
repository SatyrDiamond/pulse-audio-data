import wave
import struct
import random
import sounddevice as sd
import obj_pulsewrite





pulse_size = 0.0022
splitnum = 32
RATE = 16000
filename = "exp_pulsereader.py"












CHUNK = 1024
f = open('files/'+filename, "rb")
sd.default.channels = 1
sd.default.samplerate = RATE
samplemake = obj_pulsewrite.writer(splitnum, pulse_size, RATE, f)
def callback(indata, outdata, frames, time, status):
	if status: print(status)
	chunk = b''
	for x in samplemake.frame_chunk(frames): chunk += struct.pack('b', int(x * 128.0))
	outdata[:] = chunk

with sd.RawStream(channels=1, dtype='int8', callback=callback):
	sd.sleep(int(100000000000))



#with wave.open("output_wavfile.wav", "wb") as handle:

#	chunk = b''
#	for i in samplemake.frame(): 
#		chunk += struct.pack('h', int(i * 32767.0))
#	sd.play(chunk, RATE)