import base64
import json
import block
from rle import derle

def transposedict(d):
    ks,vs=zip(*filter(lambda x:x[0][:4]=='byte',d.items()))
    return [{k:v for k,v in zip(ks,r)} for r in zip(*vs)]

def makegrid(a,size):
    w,h=map(int,size)
    if len(a)!=w*h:
        raise 'wrong size grid'
    return [a[i*w:(i+1)*w] for i in range(h)]

with open('blocks.json','r') as f:
    blocks=json.load(f)


def doublemap(f,xss):
    return [[f(x) for x in xs] for xs in xss]

def getblockname(b):
    return blocks[b['byteA']]

def getwelded(b):
    v=bin(b['byteB']+256)[3:7]
    return [v[3]=='1',v[0]=='1',v[1]=='1',v[2]=='1']

def getrotate(b):
    return b['byteC']%4

def getblockdata(b):
    return getblockname(b),getrotate(b),getwelded(b)

def decodestructure(s):
    return {
        k:derle([*base64.b64decode(v)]) for
        k,v in
        s.items()
    }

def rendergrid(grid,dims):
    # grid is {'byteA':list of tile values,...}
    # not grid of tile values
    g=makegrid(transposedict(grid),dims)
    return block.makeimage(doublemap(getblockdata,g),bsize=16,autoweld=False)