import rsv2
import rsvedit
import random

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/demo_world'

chs = rsv2.readall(f)

def printblk(b):
  print(b[0],bin(b[1] + 256)[3:],b[2],b[3],b[4])

printblk(rsvedit.getblock(chs,0,0))
b,*_ = rsvedit.getblock(chs,0,0)
for i in range(50):
  rsvedit.setblock(chs,i,0,[3,0,0,0,0])

for i in range(20,50):
  for j in range(20,50):
    rsvedit.setblock(chs,i,j,[random.randint(0,105),0,0,0,0])

for i in range(256):
  rsvedit.setblock(chs,(i % 16) * 3,-180 + (i // 16) * 3,[59,i,0,0,0])

for i in range(16):
  for j,c in enumerate(reversed(bin(i + 16)[3:])):
    rsvedit.setblock(chs,i * 3,-180 - 3 - j,[54,5 * 16,0,ord(c),0])
  rsvedit.setblock(chs,i * 3,-180 - 2,[59,1 * 16,0,0,0])

for i in range(16):
  for j,c in enumerate(reversed(bin(i + 16)[3:])):
    rsvedit.setblock(chs,-3 - j,-180 + i * 3,[54,10 * 16,0,ord(c),0])
  rsvedit.setblock(chs,-2,-180 + i * 3,[59,8 * 16,0,0,0])

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/wires'

rsv2.writeall(f,chs)

# rsv2.writeall(f,{(0,0):{
#   'pos':(0,0),
#   'genstage':150,
#   'lastrandtick':0,
#   'tiles':[[0]*4096]*5,
#   'tiledyn':b'',
#   'entity':b''
# }})