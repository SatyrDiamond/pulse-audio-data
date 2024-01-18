import wave
import struct
import random
import obj_pulsewrite





pulse_size = 0.0025
splitnum = 64
freq = 16000
filename = "exp_pulsereader.py"


f = open('files/'+filename, "rb")

audio = []
with wave.open("output_wavfile.wav", "wb") as handle:
	handle.setparams([1, 2, freq, 1764000, 'NONE', 'not compressed'])
	samplemake = obj_pulsewrite.writer(splitnum, pulse_size, freq, f)

	for i in samplemake.frame():
		audio.append(i)

	for sample in audio: 
		handle.writeframes(struct.pack('h', int( sample * 32767.0 )))