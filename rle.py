import struct

def derle(data):
  out=[]
  while len(data)>0:
    n,=struct.unpack('<b',data[:1])
    data=data[1:]
    if n==0:
      n,=struct.unpack('<i',data[:4])
      data=data[4:]
    if n>0:
      out.extend([data[0]]*n)
      data=data[1:]
    elif n<0:
      n=-n
      out.extend(data[:n])
      data=data[n:]
    elif n==0:
      raise Exception('end of rle marker')
  return out