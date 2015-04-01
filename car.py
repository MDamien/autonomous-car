from mysim import *

def take_input():
    S = {}
    while True:
        line = input()
        if 'update' in line:
            break
        k,*v = line.strip().split()
        if k == 'speedlimit':
            v = list(map(float, v))
            v = {'curr_limit':v[0], 'dist_next_limit':v[1], 'next_limit':v[2]}
        elif k == 'trafficlight':
            if len(v) == 1:
                continue
            else:
                v = {'distance':float(v[0]), 'state':v[1].lower(), 'remaining-time':float(v[2])}
        else:
            v = list(map(float, v))
            v = v[0]
        S[k] = v
    return S

def real_sim():
    DATA = []
    while True:
        S = take_input()
        T,B = take_decision(S)
        send(T,B)

        curr_limit_V = S['speedlimit']['curr_limit']
        tl_time, tl_state,tl_dist = 0,"",0
        if 'trafficlight' in S:
            tl_time = S['trafficlight']['remaining-time']
            tl_state = S['trafficlight']['state']
            tl_dist = S['trafficlight']['distance']
        DATA.append((S['time'], S['distance']/10, S['speed'],T/10-12, B/10-11, curr_limit_V,
            tl_time, 60 if tl_state == 'green' else 50, tl_dist))

        """        
        if S['distance'] > 900:
            plot(DATA)
            plante
        """

def send(T,B):
    print("throttle %d" % T)
    print("brake %d" % B)

def fake_sim():
    limits = [{
        'start':0,
        'limit':70,
    }]

    lights = [{
        'pos': 50,
        't0':1,
        'interval': 10,
    },{
        'pos': 150,
        't0':17,
        'interval': 13,
    }]

    pos = 0.
    speed = 0.
    dt = 0.1
    steps = 0
    t = 0
    energy_usage = 0

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

        curr_light = None
        for light in lights:
            if light['pos'] > pos:
                curr_light = light
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
        tl_time = 0
        tl_state = 'sdq'
        if curr_light:
            tl_time = (curr_light['t0'] + t) % curr_light['interval']*2
            if tl_time < curr_light['interval']:
                tl_state = "green"
            else:
                tl_state = "red-or-something-similar"
            params['trafficlight'] = {
                'distance': curr_light['pos']-pos,
                'state': tl_state,
                'remaining-time': curr_light['interval'] - (tl_time % curr_light['interval'])
            }
        T, B = take_decision(params)
        energy_usage += dt*(T/100*310+1)
        #print('decision', T, B)
        prev_pos, prev_speed = pos, speed
        pos, speed = one_step(pos, speed, T,B,dt)
        if curr_limit and speed > curr_limit_V+3:
            print("!!SPEEDING!!", speed," > ", curr_limit_V)
        if curr_light and prev_pos <= curr_light['pos'] <= pos:
            if tl_state == "red":
                print("!!RECKLESS-DRIVING!!", curr_light)
            else:
                print("CROSSED GREEN TRAFFIC LIGHT!")

        steps += 1
        t = steps*dt

        if steps % 20 == 0:
            print(t, pos, speed)
        DATA.append((t, speed,T/10-12, B/10-11, curr_limit_V, energy_usage/100,
            tl_time, 60 if tl_state == 'green' else 50))
    
    print("ENERGY",energy_usage)
    plot(DATA)


def dico_search(S, sl, tl):
    bmin, bmax,T, B = -MAX_BRAKE_PRCT, 100, 0, 0
    while True:
        v = bmin+(bmax-bmin)//2
        if v == bmax-1 or v == bmin or abs(v) > 100:
            break
        T, B = 0, 0
        if v > 0:
            T = v
        else:
            B = -v
        ok,_ = do_and_emergency_break_all_the_way(S['distance'], S['speed'],T,B, sl, tl)
        if ok:
            bmin = v
        else:
            bmax = v
    return T,B

def dico_search_tl(S, sl, tl):
    bmin, bmax,T, B = 20, 100, 0, 0
    while True:
        v = bmin+(bmax-bmin)//2
        if v == bmax-1 or v == bmin or abs(v) > 100:
            break
        T, B = 0, 0
        if v > 0:
            T = v
        else:
            B = -v
        ok,pass_light = do_and_emergency_break_all_the_way(S['distance'], S['speed'],T,B, sl, tl)
        if ok and pass_light:
            bmin = v
        else:
            bmax = v

    return ok, T,B

def take_decision(S):
    T = 0
    B = 0
    sl = S.get('speedlimit')
    tl = S.get('trafficlight')

    T = 100
    B = 0
    if sl:
        #ok, T,B = dico_search_tl(S, sl, tl)
        #if not ok:
        T,B = dico_search(S, sl, tl)
    return T,B

import sys
if len(sys.argv) > 1:
    fake_sim()
else:
    real_sim()