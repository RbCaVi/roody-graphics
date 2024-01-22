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