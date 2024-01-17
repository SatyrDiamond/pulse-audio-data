import wave
import numpy as np
import obj_pulseread





pulse_size = 0.0055






with wave.open('output_wavfile.wav','r') as wav_file:
	signal = wav_file.readframes(-1)
	signal = np.fromstring(signal, 'int16')

	hz = wav_file.getframerate()

	datar = obj_pulseread.read_pulse(hz, pulse_size)

	out_tab = [0]

	for t in signal:
		datar.frame(t)


