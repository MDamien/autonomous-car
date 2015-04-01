MAX_FRICTION = 0.001 #km/h
MAX_BRAKE = 19

TL_SAFE_DISTANCE = 5

 #21 kmh toute les secondes ?
MAX_THROTTLE = 17

MAX_BRAKE_PRCT = 100
import sys

def plot(data):
    out = open('out/out.csv', 'w')
    for d in data:
        out.write(','.join(map(str,d))+'\n')
    import matplotlib.pyplot as plt
    ts = list(map(lambda x: x[0], data))
    for i in range(1,len(data[0])):
        s = list(map(lambda x: x[1:], data))
        plt.plot(ts, s, label=str(i))
    plt.show()

def kmh2ms(speed):
    return speed*1000/(60*60)

def friction(speed):
    if speed < 50.:
        return speed/50*MAX_FRICTION
    return MAX_FRICTION

def final_brake(speed):
    return brake*MAX_BRAKE

def simulate(strategie, p0=0, s0=0):
    speed = s0
    pos = p0
    steps = 0
    dt = 0.1
    while True:
        throttle, brake = strategie(steps, pos, speed)
        pos, speed = one_step(pos, speed, throttle, brake, dt)
        steps += 1
        t = steps*dt
        yield t, pos, speed

def one_step(p0, s0, T, B, dt):
    T = T/100
    B = B/100
    pos = p0 + kmh2ms(s0)*dt
    accel = T*MAX_THROTTLE - B*MAX_BRAKE
    speed = s0 + accel*dt
    speed = max(0.0, speed)
    return pos, speed

def do_and_emergency_break_all_the_way(p0, s0, T, B, sl, tl):
    if sl['curr_limit'] != 0:
        if s0-3 > sl['curr_limit']:
            return False

    def strategie(steps, pos, speed):
        if steps < 3:
            return T, B
        else:
            return 0,MAX_BRAKE_PRCT

    DATA = []
    next_limit_pos = p0+sl['dist_next_limit'] if sl['dist_next_limit'] else None
    prev_pos = p0
    result = True
    for t, pos, speed in simulate(strategie, p0, s0):
        #check speeding
        if next_limit_pos and pos > next_limit_pos+10:
            break
        if sl:
            if sl['next_limit'] != 0:
                if next_limit_pos and pos >= next_limit_pos:
                    if speed > sl['next_limit']:
                        result =  False
                        break
            if sl['curr_limit'] != 0:
                if speed > sl['curr_limit']:
                    result = False
                    break

        #check traffic light
        if tl and prev_pos-TL_SAFE_DISTANCE <= p0+tl['distance'] <= pos+TL_SAFE_DISTANCE:
            state_changed = tl['remaining-time'] - t < 0
            green = tl['state'] == 'green'
            if state_changed:
                green != green
            #DATA.append((t,pos/10, t, tl['distance']/10, tl['remaining-time'], 70 if green else 80))
            if pos >= p0+tl['distance']-30 and not green:
                result = False
                break

        prev_pos = pos
        if speed < 0.1:
            break
    pass_next_light = False
    if tl:
        if pos > p0+tl['distance']:
            pass_next_light = True
    return result, pass_next_light

if __name__ == "__main__":
    print("accelerate", do_and_emergency_break_all_the_way(50, \
        99, 100, 0, {'curr_limit':100, 'next_limit':0, 'dist_next_limit':200}))
    print("accelerate 2", do_and_emergency_break_all_the_way(50, \
        200, 100, 0, {'curr_limit':100, 'next_limit':0, 'dist_next_limit':200}))
    print("accelerate 3", do_and_emergency_break_all_the_way(0, \
        100, 100, 0, {'curr_limit':1000, 'next_limit':10, 'dist_next_limit':30}))