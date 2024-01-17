
import wave
import numpy as np


class read_pulse:
	def __init__(self, hz, trigger_val):
		self.c = 20
		self.t_enter = -15000
		self.t_act = False
		self.datar = read_num(hz, trigger_val)
		self.out_tab = [0]

	def frame(self, t):
		self.out_tab[-1] += 1

		if t<self.t_enter and not self.t_act:
			self.t_act = True
			self.datar.frame(self.out_tab[-1])
			self.out_tab.append(0)

		if t>self.t_enter: 
			self.t_act = False


class countcheck:
	def __init__(self, i_value, i_max):
		self.value = i_value
		self.max = i_max
		self.ishold = False
		self.count = 0

	def check(self, value):
		value = round(value)

		if value != self.value: self.count = 0
		else: self.count += 1

		if self.count == self.max: return True
		else: return False



class binarydata:
	def __init__(self):
		self.bintable = ''
		self.data_out = bytearray(b'')

	def frame(self, outval):
		outval = outval-1
		if -1 < outval < 2: self.bintable += str(outval)

		if len(self.bintable) == 9:
			hexval = int(self.bintable[:-1], 2)
			#print(self.bintable,  str(chr(hexval))  )
			self.data_out.append(hexval)
			self.bintable = ''




class read_num:
	def __init__(self, hz, trigger_val):
		self.count = 0
		self.stage = 0
		self.filename = None
		self.data_out = bytearray(b'')
		self.hz = hz
		self.trigger_val = trigger_val

		self.check_headstart = countcheck(5, 20)
		self.check_datastart = countcheck(6, 10)
		self.check_end = countcheck(12, 20)
		self.binf_filename = binarydata()
		self.binf_datanum = binarydata()
		self.binf_datachunk = binarydata()

		self.binf_datamode = 'num'
		self.hasdata = False
		self.hasnum = False
		self.datachunks = {}
		self.chunknum = 0

	def frame(self, outval):
		outval = ((outval/self.hz)/(self.trigger_val/2))
		outval = round(outval)

		if self.check_headstart.check(outval):
			print('DATA FOUND')
			self.binf_filename = binarydata()
			self.stage = 'filename'

		if self.stage == 'filename':
			self.binf_filename.frame(outval)
			if outval == 7:
				if not self.filename: self.filename = self.binf_filename.data_out.decode()
				print('FILENAME: '+self.filename)
				self.stage = 'data'
				self.check_data_num = countcheck(6, 5)
				self.check_data_data = countcheck(4, 5)
				self.hasnum = False
				self.hasdata = False
				self.datachunks = {}

		if self.stage == 'data':
			if self.check_data_num.check(outval):
				self.hasnum = True
				if self.hasdata and self.hasnum:
					self.datachunks[self.chunknum] = self.binf_datachunk.data_out
					print(bytes(self.binf_datachunk.data_out))

				self.binf_datamode = 'num'
				self.binf_datanum = binarydata()
				self.hasdata = False

			if self.check_data_data.check(outval):
				self.hasdata = True
				self.chunknum = int.from_bytes(self.binf_datanum.data_out, 'big')
				print('CHUNK #'+str(self.chunknum)+' |', end=' ')
				self.binf_datamode = 'raw'
				self.binf_datachunk = binarydata()
				self.datachunks[self.chunknum] = b''

			if self.binf_datamode == 'num':
				self.binf_datanum.frame(outval)

			if self.binf_datamode == 'raw':
				self.binf_datachunk.frame(outval)

		if self.check_end.check(outval):

			if self.hasdata and self.hasnum:
				self.datachunks[self.chunknum] = self.binf_datachunk.data_out
				print(bytes(self.binf_datachunk.data_out))

			print('end')

			self.stage = 'filename'

			try: 
				numchunks = len(self.datachunks)
				lenlist = [len(self.datachunks[x]) for x in range(numchunks-1)]

				if all(x==lenlist[0] for x in lenlist):
					outdata = b''
					for num in range(numchunks): outdata += self.datachunks[num]
					f = open("out/"+self.filename, "wb")
					f.write(outdata[:-1])
					f.close()
			except:
				print("error")






