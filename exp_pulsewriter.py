import wave
import struct
import random





pulse_size = 0.0055/4

splitnum = 64

filename = "VENDOR.DOC"




class pulseclick:
	def __init__(self):
		self.stage = 0
		self.curpoint = 0

	def frame(self):

		valmul = 2

		if self.stage == 0: 
			self.curpoint -= 0.1*valmul
			if self.curpoint < -0.9: self.stage = 1

		if self.stage == 1: 
			self.curpoint += 0.2*valmul
			if self.curpoint > 0.5: self.stage = 2

		if self.stage == 2: 
			self.curpoint *= 0.92
			if self.curpoint < 0: self.stage = 3

		return self.curpoint

	def reset(self):
		self.stage = 0


class pb_bitstream:
	def __init__(self, i_bytes):
		self.bytesdata = i_bytes+b'\x00'
		self.b_len = len(self.bytesdata)
		self.end = False
		self.count = 8
		self.b_bytenum = 0

	def get(self, pb_obj):
		self.count -= 1
		if self.count < 0: 
			self.b_bytenum += 1
			self.count = 8
		if self.b_len > self.b_bytenum: 
			return False, (self.bytesdata[self.b_bytenum] >> self.count) & 1
		else: 
			return True, 100000000

class pb_bitstream_chunk:
	def __init__(self, pb_obj, changestage):
		self.pb_bitstream = pb_bitstream(pb_obj.chunked_data[pb_obj.current_chunk])
		self.changestage = changestage

	def get(self, pb_obj):
		is_end, outval = self.pb_bitstream.get(pb_obj)

		if is_end:
			if pb_obj.current_chunk < len(pb_obj.chunked_data)-1:
				pb_obj.stage = self.changestage
				pb_obj.current_chunk += 1

		return is_end, outval


class counter:
	def __init__(self, i_max, i_val):
		self.max = i_max
		self.outv = i_val
		self.count = self.max

	def get(self, pb_obj):
		self.count -= 1
		if self.count == 0: 
			self.count = self.max
			return True, self.outv
		else: 
			return False, self.outv

class pulsebreak:
	def __init__(self, filename, i_bytes, splitnum):
		self.bytesdata = i_bytes+b'\x00'
		self.stage = 0
		self.count = 100
		self.b_bytenum = 0
		self.b_bitnum = 0
		self.end = False
		self.splitnum = splitnum
		self.current_chunk = 0
		self.chunked_data = [self.bytesdata[i:i + self.splitnum] for i in range(0, len(self.bytesdata), self.splitnum)]
		self.filename = self.splitnum.to_bytes(2, 'big') + len(self.chunked_data).to_bytes(2, 'big') + filename.encode()

		print(len(self.chunked_data), 'chunks')

		self.pb_bitstream = pb_bitstream(self.bytesdata)
		self.currentstate = counter(1400, 3)

	def get(self):

		is_end = False

		while not self.end:

			is_end, outval = self.currentstate.get(self)
			if not is_end: return outval
			else: self.stage += 1

			if is_end: 

				self.chunkdata = self.chunked_data[self.current_chunk]

				if self.stage == 1: self.currentstate = counter(64, 4)
				elif self.stage == 2: self.currentstate = pb_bitstream(self.filename)
				elif self.stage == 3: self.currentstate = counter(10, 6)

				elif self.stage == 4: self.currentstate = counter(6, 5)
				elif self.stage == 5: self.currentstate = pb_bitstream(self.current_chunk.to_bytes(2, 'big') )
				elif self.stage == 6: self.currentstate = counter(6, 3)
				elif self.stage == 7: self.currentstate = pb_bitstream_chunk(self, 3)
				elif self.stage == 8: self.currentstate = counter(64, 11)
				else: self.end = True








f = open(filename, "rb")
numberd = pulsebreak(filename, f.read(), splitnum)







freq = 16000

audio = []
with wave.open("output_wavfile.wav", "wb") as handle:
	handle.setparams([1, 2, freq, 1764000, 'NONE', 'not compressed'])
	pulser = pulseclick()

	pulse_size_o = (freq*pulse_size/2)

	pointbreak = 0
	pointbreakactive = False

	samplecount = 0

	while not numberd.end:
		if (samplecount % int(pulse_size_o) ) == 0: 
			if pointbreak == 0: 
				pulser.reset()
				pointbreak = numberd.get()
			else: pointbreak -= 1

		audio.append(pulser.frame())
		samplecount += 1

	for sample in audio: 
		handle.writeframes(struct.pack('h', int( sample * 32767.0 )))