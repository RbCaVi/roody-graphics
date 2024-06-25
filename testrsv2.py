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

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/wires'

rsv2.writeall(f,chs)

