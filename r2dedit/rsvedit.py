from rsv2 import Chunk
import typing

Chunks: typing.TypeAlias = dict[tuple[int,int],Chunk]
Block: typing.TypeAlias = tuple[int,int,int,int,int]

def getblock(chs: Chunks, x: int, y: int) -> Block:
  cx,bx = divmod(x,64)
  cy,by = divmod(y,64)
  
  ch = chs[(cx,cy)]['tiles']
  
  bi = bx + by * 64
  
  b = tuple(g[bi] for g in ch)

  assert len(b) == 5
  
  return b

def setblock(chs: Chunks, x: int, y: int, b: Block) -> None:
  cx,bx = divmod(x,64)
  cy,by = divmod(y,64)
  
  ch = chs[(cx,cy)]['tiles']
  
  bi = bx + by * 64
  
  for bb,g in zip(b,ch):
    g[bi] = bb