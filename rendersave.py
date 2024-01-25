import struct
from rle import derle
from renderblocks import rendergrid

# filesize is missing 4 bytes
# all offsets relative to the header (except loc_offset?) are shifted by 4 bytes

# all V2D types have 4 bytes at the start for some reason

def decodechunklocations(data):
  locs=[dict(zip(['posX','posY','offset'],t[1:])) for t in struct.iter_unpack("<iqqI",data)] # the 1st is padding
  return locs

def decodechunkheader(data):
  t=struct.unpack("<IiqqIIIIIIII",data)
  ch=t[:1]+t[2:] # the 2nd is padding
  return dict(zip([
    'len',
    'posX','posY',
    'gen_stage','last_rand_tick',
    'grid_offset','grid_size',
    'tiledata_offset','tiledata_size',
    'entities_offset','entities_size'
  ],ch))

chunkheadersize=struct.calcsize("<IiqqIIIIIIII")

def getchunkheader(loc,chunks_offset):
  offset=chunks_offset+loc['offset']+4
  return decodechunkheader(savedata[offset:offset+chunkheadersize])

def decodetilegridheader(data):
  t=struct.unpack("<IiqqIIIIIIIIIIIIIIIIII",data)
  th=t[:1]+t[2:] # the 2nd is padding
  return dict(zip([
    'len',
    'boundX','boundY', # always 64
    'A_offset','A_size',
    'B_offset','B_size',
    'C_offset','C_size',
    'D_offset','D_size',
    'E_offset','E_size', # the rest are ignored
  ],th))

tilegridheadersize=struct.calcsize("<IiqqIIIIIIIIIIIIIIIIII")

def gettilegrid(savedata,ch,chunks_offset):
  offset=chunks_offset+ch['grid_offset']+4
  tilegrid=savedata[offset:offset+ch['grid_size']]
  tilegridheader=decodetilegridheader(tilegrid[:tilegridheadersize])
  offsetA=tilegridheader['A_offset']
  sizeA=tilegridheader['A_size']
  dataA=tilegrid[offsetA:offsetA+sizeA]
  tilesA=derle(dataA)
  offsetB=tilegridheader['B_offset']
  sizeB=tilegridheader['B_size']
  dataB=tilegrid[offsetB:offsetB+sizeB]
  tilesB=derle(dataB)
  offsetC=tilegridheader['C_offset']
  sizeC=tilegridheader['C_size']
  dataC=tilegrid[offsetC:offsetC+sizeC]
  tilesC=derle(dataC)
  offsetD=tilegridheader['D_offset']
  sizeD=tilegridheader['D_size']
  dataD=tilegrid[offsetD:offsetD+sizeD]
  tilesD=derle(dataD)
  offsetE=tilegridheader['E_offset']
  sizeE=tilegridheader['E_size']
  dataE=tilegrid[offsetE:offsetE+sizeE]
  tilesE=derle(dataE)
  return {
    "byteA":tilesA,
    "byteB":tilesB,
    "byteC":tilesC,
    "byteD":tilesD,
    "byteE":tilesE,
    "posX":ch["posX"],
    "posY":ch["posY"]
  }

def gettilegrids(savedata):
  version,filesize,_,regionX,regionY,loc_offset,loc_size,chunks_offset,chunks_size=struct.unpack("<iIiqqIIII",savedata[:44])

  chunklocations=decodechunklocations(savedata[loc_offset:loc_offset+loc_size])

  chunkheaders=[getchunkheader(loc,chunks_offset) for loc in chunklocations]

  tilegrids=[]
  for ch in chunkheaders:
    try:
      tilegrid=gettilegrid(savedata,ch,chunks_offset)
      print(tilegrid['posX'],tilegrid['posY'])
      tilegrids.append(tilegrid)
    except Exception as e:
      offset=chunks_offset+ch['grid_offset']+4
      tilegrid=savedata[offset:offset+ch['grid_size']]
      tilegridheader=decodetilegridheader(tilegrid[:tilegridheadersize])
      print('tgerr',e,tilegridheader,tilegridheader['len'])
      print('tgerr',tilegridheader['len'])
      print('tgerr',len(tilegrid[:tilegridheader['len']]))
      print('tgerr',tilegridheader['A_size']+tilegridheader['B_size']+tilegridheader['C_size']+tilegridheader['D_size']+tilegridheader['E_size']+tilegridheadersize)

  return tilegrids

if __name__=='__main__':
  import sys
  import os
  savefolder=sys.argv[1]

  d=os.path.join(savefolder,'images')
  os.makedirs(d,exist_ok=True)

  for filename in os.listdir(savefolder):
    if not filename.endswith('.rsv'):
      continue
    print(filename)
    savefile=os.path.join(savefolder,filename)
    with open(savefile,'rb') as f:
      savedata=f.read()

    try:
      tilegrids=gettilegrids(savedata)
      for tilegrid in tilegrids:
        try:
          im,x,y=rendergrid(tilegrid,(64,64)),tilegrid['posX'],tilegrid['posY']
        except Exception as e:
          print('rgerr',e,x,y)
        im.save(os.path.join(d,f"{x}_{y}.png"))
    except Exception as e:
      print('err',e)
    