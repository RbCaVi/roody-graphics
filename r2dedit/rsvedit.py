from rsv2 import Chunk

def getblock(chs: dict[tuple[int,int],Chunk], x: int, y: int) -> tuple[int,int,int,int,int]:
  cx,bx = divmod(x,64)
  cy,by = divmod(y,64)
  
  ch = chs[(cx,cy)]['tiles']
  
  bi = bx + by * 64
  
  b = tuple(g[bi] for g in ch)

  assert len(b) == 5
  
  return b

def setblock(chs: dict[tuple[int,int],Chunk], x: int, y: int, b: tuple[int,int,int,int,int]) -> None:
  cx,bx = divmod(x,64)
  cy,by = divmod(y,64)
  
  ch = chs[(cx,cy)]['tiles']
  
  bi = bx + by * 64
  
  for bb,g in zip(b,ch):
    g[bi] = bb