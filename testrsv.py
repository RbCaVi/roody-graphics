import rsv
f='/home/rvail/Desktop/games/roody 0.9.8/saves/creative/r0_-1.rsv'
with open(f,'rb') as f:
  data=f.read()

s=rsv.readsave(data)
data2=rsv.encode(s)
print(*map(len,[data,data2]))

import difflib
matches=difflib.SequenceMatcher(None,data,data2).get_matching_blocks()
m,*matches=matches
for match in matches:
	print('data',data[m.a+m.size:match.a])
	print('data2',data2[m.b+m.size:match.b])
	print(data[match.a:match.a+match.size])
	m=match

#print(*difflib.diff_bytes(difflib.unified_diff,[data],[data2]))
#print(*difflib.diff_bytes(difflib.context_diff,[data],[data2]))

# https://stackoverflow.com/a/53818532
def recursive_compare(d1, d2, level='root'):
    if isinstance(d1, dict) and isinstance(d2, dict):
        if d1.keys() != d2.keys():
            s1 = set(d1.keys())
            s2 = set(d2.keys())
            print('{:<20} + {} - {}'.format(level, s1-s2, s2-s1))
            common_keys = s1 & s2
        else:
            common_keys = set(d1.keys())

        for k in sorted(common_keys):
            recursive_compare(d1[k], d2[k], level='{}.{}'.format(level, k))

    elif isinstance(d1, list) and isinstance(d2, list):
        if len(d1) != len(d2):
            print('{:<20} len1={}; len2={}'.format(level, len(d1), len(d2)))
        common_len = min(len(d1), len(d2))

        for i in range(common_len):
            recursive_compare(d1[i], d2[i], level='{}[{}]'.format(level, i))

    else:
        if d1 != d2:
            print('{:<20} {} != {}'.format(level, d1, d2))

s2=rsv.readsave(data2)

print(recursive_compare(s,s2))

import sys
sys.exit()

data3=rsv.encode(s2)

print(data2==data3)

print('len',*map(len,[data2,data3]))

import difflib
matches=difflib.SequenceMatcher(None,data2,data3).get_matching_blocks()
m,*matches=matches
for match in matches:
	print('data2',data2[m.a+m.size:match.a])
	print('data3',data3[m.b+m.size:match.b])
	print(data[match.a:match.a+match.size])
	m=match