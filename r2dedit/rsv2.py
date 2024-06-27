import glob

import os

import struct

import rle
import collections

import typing

hf = '<I4s2qIIII'
lf = '<2qI4x'
cf = '<I4s2qIiIIIIII'
gf = '<I4s2q10I32x'

def unpackh(fmt: str, data: bytes) -> tuple[typing.Any,...]:
  return struct.unpack(fmt,data[:struct.calcsize(fmt)])

def unpacki(fmt: str, data: bytes) -> typing.Iterable[tuple[typing.Any,...]]:
  return struct.iter_unpack(fmt,data)

class Chunk(typing.TypedDict):
  pos: tuple[int,int]
  genstage: int
  lastrandtick: int
  tiles: tuple[list[int],list[int],list[int],list[int],list[int]]
  tiledyn: bytes
  entity: bytes

def read(fname: str) -> dict[tuple[int,int],Chunk]:
  with open(fname,'rb') as f:
    data = f.read()
  
  version = struct.unpack('<i',data[:4])
  data = data[4:] # ignore version
  
  fsz,fmag,fx,fy,loff,lsz,coff,csz = unpackh(hf,data)
  #assert fmag == b'.rsv'
  
  #print('fpos',fx,fy)
  #print(fsz,fmag,fx,fy,loff,lsz,coff,csz)
  
  ldata = data[loff:loff + lsz]
  locs = unpacki(lf,ldata)
  
  cdata = data[coff:coff + csz]
  
  chs: dict[tuple[int,int],Chunk] = {}
  for loc in locs:
    lx,ly,ccoff = loc
    #print('dcpos',lx,ly,ccoff)
    ccdata = cdata[ccoff:]
    csz,cmag,cx,cy,gst,lrtk,goff,gsz,doff,dsz,eoff,esz = unpackh(cf,ccdata)
    #print('cpos',cx,cy,'cdat',gst,lrtk)
    #assert cmag == b'chnk'
    assert fx * 32 + lx == cx
    assert fy * 32 + ly == cy
    gdata = ccdata[goff:goff + gsz]
    gsz,gmag,gw,gh,*toffsz = unpackh(gf,gdata)
    #assert gmag == b'tile'
    assert gw == 64
    assert gh == 64
    toff = toffsz[::2]
    tsz = toffsz[1::2]
    tdata = [rle.derle(gdata[off:off + sz]) for off,sz in zip(toff,tsz)]
    for tg in tdata:
      assert len(tg) == 64 * 64
    tdatat = tuple(tdata)
    assert len(tdatat) == 5
    #print('til',tdata)
    ddata = ccdata[doff:doff + dsz]
    edata = ccdata[eoff:eoff + esz]
    #print('dyn',ddata)
    #print('ent',edata)
    #print()
    chs[(cx,cy)] = {
      'pos':(cx,cy),
      'genstage':gst,
      'lastrandtick':lrtk,
      'tiles':tdatat,
      'tiledyn':ddata,
      'entity':edata
    }
  
  return chs

def readall(savedir: str) -> dict[tuple[int,int],Chunk]:
  chs = {}
  for f in glob.glob(os.path.join(savedir,'r*_*.rsv')):
    #print(f)
    newchs = read(f)
    for cpos in newchs:
      assert cpos not in chs
    chs.update(newchs)
  
  return chs

class ChunkP(typing.TypedDict):
  pos: tuple[int,int]
  lpos: tuple[int,int]
  genstage: int
  lastrandtick: int
  tiles: tuple[list[int],list[int],list[int],list[int],list[int]]
  tiledyn: bytes
  entity: bytes

def writeall(savedir: str, chs: dict[tuple[int,int],Chunk]) -> None:
  fs: dict[tuple[int,int],dict[tuple[int,int],Chunk]] = collections.defaultdict(dict)
  
  for (cx,cy),ch in chs.items():
    fx,lx = divmod(cx, 32)
    fy,ly = divmod(cy, 32)
    fs[(fx,fy)][(lx,ly)]=ch
  
  for (fx,fy),fchs in fs.items():
    ls = b''
    cs = b''
    for (lx,ly),fch in fchs.items():
      l = struct.pack(lf,lx,ly,len(cs))
      ls += l
      chsz = struct.calcsize(cf)
      c = b''
      ts = b''
      offs = []
      szs = []
      thsz = struct.calcsize(gf)
      for t in fch['tiles']:
        tr = rle.torle(t)
        offs.append(len(ts) + thsz)
        szs.append(len(tr))
        ts += tr
      offsz = [x for off,sz in zip(offs,szs) for x in (off,sz)]
      th = struct.pack(gf,len(ts) + thsz,b'tile',64,64,*offsz)
      toff = len(c) + chsz
      tsz = len(th + ts)
      c += th + ts
      doff = len(c) + chsz
      dsz = len(fch['tiledyn'])
      c += fch['tiledyn']
      eoff = len(c) + chsz
      esz = len(fch['entity'])
      c += fch['entity']
      cx,cy = fch['pos']
      chd = struct.pack(cf,len(c) + chsz,b'chnk',cx,cy,fch['genstage'],fch['lastrandtick'],toff,tsz,doff,dsz,eoff,esz)
      cs += chd + c
    fhsz = struct.calcsize(hf)
    fdata = b''
    loff = len(fdata) + fhsz
    lsz = len(ls)
    fdata += ls
    coff = len(fdata) + fhsz
    csz = len(cs)
    fdata += cs
    fh = struct.pack(hf,len(fdata) + fhsz,b'.rsv',fx,fy,loff,lsz,coff,csz)
    fdata = struct.pack('<i',1) + fh + fdata
    f2 = os.path.join(savedir,f'r{fx}_{fy}.rsv')
    with open(f2,'wb') as f3:
      f3.write(fdata)