import struct,sys
from bitarray import bitarray
from array import array
def decompress(data):
	global bits
	bits=None

	marker=data[:4]
	if marker!='KCDC':
		raise NotImplementedError("Only KCDC supported")
	outlength=struct.unpack('!L',data[4:8])[0]
	print 'outlength=',outlength

	END_OF_FILE=bitarray(endian='little')
	END_OF_FILE.frombytes('\xFF\xFF\xFF')

	output=array('B')

	def readBits(): # ugly hack. make this a class!
		global bits,offset
		try:
			bits
			if bits is None:
				raise NameError() # HAX
		except NameError: # first run. 
			offset=9
			bits=bitarray(endian='little')
		if len(bits)<40:
			missing=(40-len(bits))//8
			if missing>0:
				newbits=bitarray(endian='little')
				newbits.frombytes(data[offset:offset+missing])
				bits.extend(newbits)
				offset+=missing

	def consume(numbits):
		global bits
		bits=bits[numbits:]

	def extract(numbits):
		readBits()
		print 'extracting',numbits,bits[:numbits]
		b=bits[:numbits].tobytes()
		struct_format='B'
		if numbits>8:
			if numbits>16:
				struct_format='L'
				if len(b)==3:
					b=b+'\0'
			else:
				struct_format='H'

		value=struct.unpack('<'+struct_format,b)[0]
		consume(numbits)
		return value

	readBits()
	while True:
		readBits()
		if bits[0:24]==END_OF_FILE:
			consume(24)
			break
		if bits[0]==0: # raw output
			consume(1)
			output.append(extract(8))
		else:
			if bits[0:4]==bitarray('1111',endian='little'):
				print 'matched 1111'
				copy_size=3
				consume(4)
				look_back=extract(20)+0x1241
			elif bits[0:4]==bitarray('1110',endian='little'):
				print 'matched 1110'
				copy_size=2
				consume(4)
				look_back=extract(12)+0x241
			elif bits[0:3]==bitarray('110',endian='little'):
				print 'matched 110'
				copy_size=2
				consume(3)
				look_back=extract(9)+0x41
			elif bits[0:2]==bitarray('10',endian='little'):
				print 'matched 10'
				copy_size=2
				consume(2)
				look_back=extract(6)+1
			matches=bits[:12].search(bitarray('0'),1)
			if not matches:
				raise ValueError('lookback with no 0 in 12 bits!')
			else:
				print 'found 0 at {} in {}'.format(matches[0],bits[:12])
			pos=matches[0]
			consume(1+pos)
			copy_size+=(1<<pos)-1
			if pos>0:
				copy_size+=extract(pos)
			print 'look_back={} copy_size={}'.format(look_back,copy_size)
			for i in range(copy_size):
				output.append(output[-look_back])
			if verify is not None:
				if output.tostring()!=verify[:len(output)]:
					print 'Diverged at byte',len(output)


	#TODO: compare against header
	print 'length of output',len(output)
	return output.tostring()


if __name__ == '__main__':
	with open(infile,'rb') as f:
		data=f.read()
	outdata=decompress(data)
	with open(outfile,'wb') as f:
		f.write(outdata)
