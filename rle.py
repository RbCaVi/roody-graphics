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

maxnint=(1<<31) # the maximum negative value that can fit in a signed int32
maxbyte=(1<<7)-1 # the maximum value that can fit in a signed int8/byte

def getintbytes(i):
  try:
    return struct.pack('<b',i)
  except:
    return struct.pack('<bi',0,i)

def getuniqueseg(b):
  if len(b)==0:
    return b''
  return getintbytes(len(b))+b

def getrepeatseg(count,b):
  if count==0:
    return b''
  return getintbytes(count)+bytes([b])

def torle(data,addsep=False):
  out=b''
  repeatbyte=data[0]
  repeatcount=0
  uniquebytes=b''
  if type(data)==str:
    data=bytes(data,'utf-8')
  for byte in data:
    if byte==repeatbyte and repeatcount<maxnint:
      repeatcount+=1
    else:
      if repeatcount<=2:
        for c in [repeatbyte]*repeatcount:
          uniquebytes+=c
          if len(uniquebytes)>=maxnint:
            print('WARNING: 2 GB OF UNIQUE DATA')
            out+=getuniqueseg(uniquebytes)
            uniquebytes=b''
      else:
        out+=getuniqueseg(uniquebytes)
        uniquebytes=b''
        out+=getrepeatseg(repeatcount,repeatbyte)
        repeatbyte=None
        repeatcount=0
  if repeatcount<=2:
    for c in [repeatbyte]*repeatcount:
      uniquebytes+=c
      if len(uniquebytes)>=maxnint:
        print('WARNING: 2 GB OF UNIQUE DATA')
        out+=getuniqueseg(uniquebytes)
        uniquebytes=b''
  out+=getuniqueseg(uniquebytes)
  out+=getrepeatseg(repeatcount,repeatbyte)
  if addsep:
    # push stream end marker
    out+=b'\0\0\0\0\0'
  return out