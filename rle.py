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

def torle(data,addsep=False):
  out=b''
  uniqueseg={"count":0,"parts":[]}
  repeatseg={"count":0,"value":-1}
  repeatbyte=None
  repeatcount=0
  uniquebytes=b''
  if type(data)==str:
    data=bytes(data,'utf-8')
  for byte in data:
    if byte==repeatbyte and repeatcount<maxint:
      repeatcount+=1
    else:
      if repeatcount<=2:
        for c in [repeatbyte]*repeatcount:
          uniquebytes+=c
          if len(uniquebytes)>maxnint:
            out+=getintbytes(len(uniquebytes))
            out+=uniquebytes
            uniquebytes=b''
      else:
        out+=getintbytes(len(uniquebytes))
        out+=uniquebytes
        uniquebytes=b''
        

  for c in data:
    if repeatseg["value"]==c and repeatseg["count"]<maxint:
      repeatseg["count"]+=1
    else:
      if repeatseg["count"]<3:
        for _ in range(repeatseg["count"]):
          uniqueseg["parts"].append(repeatseg["value"])
          uniqueseg["count"]-=1
          if -uniqueseg["count"]>maxint: # because people will definitely put 2gb of random data into this
            #console.log('why would you put 2gb of unique data?',uniqueseg)
            out+=getsegbytes(uniqueseg)
            uniqueseg={"count":0,"parts":[]}
        repeatseg={"count":1,"value":c}
      else:
        out+=getsegbytes(uniqueseg)
        out+=getsegbytes(repeatseg)
        uniqueseg={"count":0,"parts":[]}
        repeatseg={"count":0,"value":c}
      
  if repeatseg["count"]<3:
    for _ in range(repeatseg["count"]):
      uniqueseg["parts"].append(repeatseg["value"])
      uniqueseg["count"]-=1
      if -uniqueseg["count"]>maxint: # because people will definitely put 2gb of random data into this
        out+=getsegbytes(uniqueseg)
        uniqueseg={"count":0,"parts":[]}
    repeatseg={"count":0,"value":-1}
  out+=getsegbytes(uniqueseg)
  out+=getsegbytes(repeatseg)
  if addsep:
    # push stream end marker
    out+=b'\0\0\0\0\0'
  return out



def getsegbytes(seg):
  print(seg)
  out=b''
  count=seg["count"]
  if count<0:
    # unique
    if -count>maxbyte:
      out+=bytes([0,count>>24&255,count>>16&255,count>>8&255,count>>0&255])
    else:
      out+=bytes([count])
    out+=bytes(seg["parts"])
  elif count>0:
    # repeat
    if count>maxbyte:
      out+=bytes([0,count>>24&255,count>>16&255,count>>8&255,count>>0&255])
    else:
      out+=bytes([count])
    out+=bytes([seg["value"]])
  return out # otherwise empty