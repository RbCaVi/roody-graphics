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

def parsesmp(smpdata):
    s,smp=getsmpvalue(smpdata)
    if len(s.strip())>0:
        raise Exception(f'probably not a valid smp: "{s}" was at the end')
    return smp

def renderstructure(smp):
    pieces=[
        makegrid(
            transposedict({
                k:[[x,bin(x+256)[3:]][0] for x in derle([*base64.b64decode(v)])] for
                k,v in
                x['storage_grid']['tiles'].items()
            }),
            x['storage_grid']['dimensions_insertable'].split(',')
        ) for
        x in
        smp['pieces']
    ]

    pims=[block.makeimage(doublemap(lambda x:(getblockname(x),getrotate(x),getwelded(x)),piece),bsize=16,autoweld=False) for piece in pieces]
    return pims

if __name__=='__main__':
    import sys
    f=sys.argv[0]

    with open(f,'r') as file:
        smpdata=file.read()

    smp=parsesmp(smpdata)

    pims=renderstructure(smp)
    [i.show() for i in pims]