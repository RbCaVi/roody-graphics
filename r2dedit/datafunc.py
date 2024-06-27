def capitalize(s:str) -> str:
    s=s[0].upper()+s[1:]
    return s

def plural(s:str) -> str:
    if s.endswith('y'): # just in case
        s=s[:-1]+'ie'
    s+="s"
    return s

def past(s:str) -> str:
    if s.endswith('e'):
        s=s[:-1]
    s+="ed"
    return s