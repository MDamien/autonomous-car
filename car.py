from mysim import *

def take_input():
    S = {}
    while True:
        line = input()
        if 'update' in line:
            break
        k,*v = line.strip().split()
        v = list(map(float, v))
        if k == 'speedlimit':
            v = {'curr_limit':v[0], 'dist_next_limit':v[1], 'next_limit':v[2]}
        else:
            v = v[0]
        S[k] = v
    return S

def real_sim():
    while True:
        S = take_input()
        T,B = take_decision(S)
        send(T,B)

def send(T,B):
    print("throttle %d" % T)
    print("brake %d" % B)

def fake_sim():
    limits = [{
        'start':0,
        'limit':130,
    },{
        'start':500,
        'limit':70,
    },{
        'start':700,
        'limit':50,
    },{
        'start':1000,
        'limit':100,
    },{
        'start':1450,
        'limit':30,
    }]
    pos = 0.
    speed = 0.
    dt = 0.1
    steps = 0
    t = 0

    DATA = []

    while pos < 1000:
        curr_limit = None
        next_limit = None
        max_start = -1
        for limit in limits:
            if limit['start'] < pos:
                if limit['start'] > max_start:
                    max_start = limit['start']
                    curr_limit = limit
            if limit['start'] > pos:
                next_limit = limit
                break
        params = {
            'time': t,
            'distance': pos,
            'speed': speed,
        }
        curr_limit_V = curr_limit['limit'] if curr_limit else 0
        next_limit_V = next_limit['limit'] if next_limit else 0
        if curr_limit:
            params['speedlimit'] = {
                'curr_limit': curr_limit['limit'],
                'next_limit': next_limit['limit'] if next_limit else 0,
                'dist_next_limit': next_limit['start']-pos if next_limit else 0,
            }
        T, B = take_decision(params)
        #print('decision', T, B)
        pos, speed = one_step(pos, speed, T,B,dt)
        #print("results",pos, speed)

        steps += 1
        t = steps*dt

        DATA.append((t, speed,T/4+12, B/4+11, curr_limit_V))
    plot(DATA)

def dico_search(S, sl):
    bmin, bmax,T, B = -100, 100, 0, 0
    while True:
        v = bmin+(bmax-bmin)//2
        if v == bmax-1 or v == bmin or abs(v) > 100:
            break
        T, B = 0, 0
        if v > 0:
            T = v
        else:
            B = -v
        ok = do_and_emergency_break_all_the_way(S['distance'], S['speed'],T,B, sl)
        if ok:
            bmin = v
        else:
            bmax = v
    return T,B

def take_decision(S):
    T = 0
    B = 0
    sl = S.get('speedlimit')

    T = 100
    B = 0
    if sl:
        T,B = dico_search(S, sl)
    return T,B

import sys
if len(sys.argv) > 5:
    fake_sim()
else:
    real_sim()