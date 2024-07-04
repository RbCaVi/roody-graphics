def getblock(chs,x,y):
  cx,bx = divmod(x,64)
  cy,by = divmod(y,64)
  
  ch = chs[(cx,cy)]['tiles']
  
  bi = bx + by * 64
  
  b = [g[bi] for g in ch]
  
  return b

def setblock(chs,x,y,b):
  cx,bx = divmod(x,64)
  cy,by = divmod(y,64)
  
  ch = chs[(cx,cy)]['tiles']
  
  bi = bx + by * 64
  
  for bb,g in zip(b,ch):
    g[bi] = bb