import rsv2
import rsvedit
import random

f = '/storage/emulated/0/Download/'

chs = rsv2.readall(f)

print(rsvedit.getblock(chs,0,0))
b,*_ = rsvedit.getblock(chs,0,0)
for i in range(50):
  rsvedit.setblock(chs,i,0,[b,0,0,0,0])

for i in range(20,50):
  for j in range(20,50):
    rsvedit.setblock(chs,0,i,[random.randint(0,105),0,0,0,0])

f = '/storage/emulated/0/Documents/pydroid3/'

rsv2.writeall(f,chs)