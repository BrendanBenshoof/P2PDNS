import math

dimensions = 2
size = 2L**80




def distance(p0, p1):
    deltas = map( lambda x,y: min([math.fabs(x-y),size-math.fabs(x-y)]), p0, p1)
    sqrdeltas = map(lambda x: int(x**2), deltas)
    sumdeltas = sum(sqrdeltas)
    dist = int(sumdeltas**0.5)
    return dist
    

def midpoint(p0, p1):
    deltas = map( lambda y,x: min([(x-y)%size,(size-(x-y))%size], key=math.fabs), p0, p1)
    return map(lambda x,y: x+y*0.5, p0, deltas)


def v_filter(p0, peers):
    if len(peers)>0:
        return min(peers, key=lambda x: distance(p0, x.loc))
    else:
        return None

def peer_reduce(me, peers):
    checked_peers = []
    for p in peers:
        if me.key!=p.key:
            checked_peers.append(p)
    
    peers = sorted(checked_peers, key=lambda x: -1*distance(me.loc, x.loc))
    canidate_peers = []
    for p in peers:
        if not p in canidate_peers:
            temp = canidate_peers + [p]
            best = v_filter(midpoint(p.loc,me.loc), temp)
            if best == p or best == me:
                canidate_peers = temp
    return canidate_peers

def hash2loc(hashval):
    hashint = int(hashval.key,16)
    x = hashint/size
    y = hashint%size
    return (x,y) 
