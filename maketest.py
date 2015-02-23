from bitarray import bitarray
from struct import pack

message="Hello world"


bits=bitarray(endian='little')

bits.frombytes(b'KCDC')
bits.frombytes(pack('!L',len(message)))
bits.frombytes(b'\0')

for c in message:
	bits.append(False)
	bits.frombytes(c)

for _ in range(8-len(bits)%8):
	bits.append(True)
bits.frombytes(b'\xFF'*7)

with open('test.dat','wb') as f:
	f.write(bits.tobytes())