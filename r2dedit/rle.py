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

int32min = -2147483648
int32max =  2147483647
int8min  = -128
int8max  =  127

def torle(raw):
  out = b""
  if len(raw) == 0:
    return out

  segments = []
  builder_segments = {"count":0,"similar":None,"uniques":[]}
  for r in raw:
    if r == builder_segments["similar"] and builder_segments["count"] < int32max:
      builder_segments["count"] += 1
    else:
      if builder_segments["count"] != 0:
        segments.append({**builder_segments})
      builder_segments["count"] = 1
      builder_segments["similar"] = r
      builder_segments["uniques"] = []
  if builder_segments["count"] != 0:
    segments.append({**builder_segments})

  uniqued_segments = []
  builder_uniqued = {"count":0,"similar":None,"uniques":[]}
  for s in segments:
    if s["count"] > 3:
      if builder_uniqued["count"] != 0:
        uniqued_segments.append({**builder_uniqued})
        builder_uniqued["count"] = 0
        builder_uniqued["uniques"] = []
      uniqued_segments.append({**s})
    else:
      builder_uniqued["count"] -= s["count"]
      builder_uniqued["uniques"].extend([s["similar"]] * s["count"])
  if builder_uniqued["count"] != 0:
    uniqued_segments.append({**builder_uniqued})

  for s in uniqued_segments:
    if s["count"] > 0:
      if s["count"] >= int8max:
        out += b"\0"
        out += struct.pack('<i',s["count"])
      else:
        out += struct.pack('<b',s["count"])
      out += bytes([s["similar"]])
    else:
      if s["count"] <= int8min:
        out += b"\0"
        out += struct.pack('<i',s["count"])
      else:
        out += struct.pack('<b',s["count"])
      out += bytes(s["uniques"])
  return out