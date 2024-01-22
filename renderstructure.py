import base64
import json
import block
from smp import getsmpvalue
from rle import derle
from renderblocks import rendergrid

def parsesmp(smpdata):
    s,smp=getsmpvalue(smpdata)
    if len(s.strip())>0:
        raise Exception(f'probably not a valid smp: "{s}" was at the end')
    return smp

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
    