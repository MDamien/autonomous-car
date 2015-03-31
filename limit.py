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
pos = 800
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
print(curr_limit,next_limit)