import rsv
f='/home/rvail/Desktop/games/roody 0.9.8/saves/creative/r0_-1.rsv'
with open(f,'rb') as f:
  data=f.read()

s=rsv.readsave(data)
data2=rsv.encode(s)
import difflib
print(*difflib.diff_bytes(difflib.unified_diff,data,data2))
print(*difflib.diff_bytes(difflib.context_diff,data,data2))