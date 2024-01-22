import base64
import json
import block
from smp import getsmpvalue

def derle(a):
    out=[]
    while len(a)>0:
        if a[0]<128: # positive when signed
            out.extend([a[1]]*a[0])
            a=a[2:]
        else:
            n=-(a[0]-256)
            a=a[1:]
            out.extend(a[:n])
            a=a[n:]
    return out

def transposedict(d):
    ks,vs=zip(*d.items())
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

def parsesmp(smpdata):
    s,smp=getsmpvalue(smpdata)
    if len(s.strip())>0:
        raise Exception(f'probably not a valid smp: "{s}" was at the end')
    return smp

def decodestructure(s):
    return {
        k:derle([*base64.b64decode(v)]) for
        k,v in
        s.items()
    }

def rendergrid(grid,dims):
    g=makegrid(transposedict(grid),dims)
    return block.makeimage(doublemap(getblockdata,g),bsize=16,autoweld=False)

def renderstructure(smp):
    pims=[
        rendergrid(
            x['storage_grid']['tiles'],
            x['storage_grid']['dimensions_insertable'].split(',')
        ) for x in
        smp['pieces']
    ]

    return pims

if __name__=='__main__':
    import sys
    f=sys.argv[1]

    with open(f,'r') as file:
        smpdata=file.read()

    smp=parsesmp(smpdata)

    pims=renderstructure(smp)
    d=f.rsplit('.',1)[0]
    import os
    dims=[x['storage_grid']['dimensions_insertable'] for x in smp['pieces']]
    os.makedirs(d,exist_ok=True)
    [im.save(d+'/'+str(i)+".png") for i,im in enumerate(pims)]
    assert all(x == dims[0] for x in dims) # all tiles are the same size
    #structure
    