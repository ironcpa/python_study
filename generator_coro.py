def gen_func():
    for i in ['a', 'b', 'c']:
        yield i

class gen_class:
    def __init__(self, list):
        self.list = list
    
    def __iter__(self):
        for i in self.list:
            yield i
            
def simple_coroutine():
    print('-> coro started')
    x = yield
    print('-> coro gets', x)

def simple_coroutine2(a):
    print('-> started: a', a)
    b = yield a
    print('-> received: b', b)
    c = yield a + b
    print('-> received: c', c)

# my test version of coroutine
def averager():
    a = yield 1
    b = yield 2
    c = yield 3
    print(a + b + c)

def averager2():
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield average
        total += term
        count += 1
        average = total / count

# decorator for auto priming generator
from functools import wraps
def coroutine(func):
    """Decorator: primes 'func' by advancing to first 'yield'"""
    @wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return primer

@coroutine
def averager3():
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield average
        total += term
        count += 1
        average = total / count

'''========================
How to Stop Coroutines?
    send sentinel value
        generator.send(unhandlerble_value)
    send StopIteration
        generator.throw(StopIteration)
========================'''

class DemoException(Exception):
    """for stop demo"""

def demo_exc_handling():
    print('-> coroutine started')
    while True:
        try:
            x = yield
        except DemoException:
            print('*** DemoException handled. Continue...')
        else:
            print('-> coroutine received: {!r}'.format(x))
    raise RuntimeError('This line sould never run')

from collections import namedtuple
Result = namedtuple('Result', 'count average')
def averager4():
    """coroutine that return value"""
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield average
        if term is None:
            break
        total += term
        count += 1
        average = total / count
    return Result(count, average)
    # returned value can not be get like
    #   r = co.send(None)
    # it's get through StopIteration object

# below is how to get return value from coroutine
"""
>>> c = averager4()
>>> next(c)
>>> c.send(5)
>>> c.send(6)
>>> try:
>>>     c.send(None)
>>> except StopIteration as ex:
>>>     r = ex.value
>>> print(result)
"""

"""
from Fluent Python 
Using yield from
The first thing to know about yield from is that it is a completely new language con‐
struct. It does so much more than yield that the reuse of that keyword is arguably
misleading. Similar constructs in other languages are called await and that is a much
better name because it conveys a crucial point: when a generator gen calls yield from
subgen() , the subgen takes over and will yield values to the caller of gen ; the caller will
in effect drive subgen directly. Meanwhile gen will be blocked, waiting until subgen
terminantes 5 .
"""
# yield from is simple for loops to yield elements
"""
>>> def gen():
...     for c in 'AB':
...         yield c
...     for i in range(1, 3):
...         yield i
>>> def gen():
...     yield from 'AB'
...     yield from range(1, 3):
"""

import asyncio
# eazy communication chennel btwn generators
def caller(data):
    results = {}
    for k, values in data.items():
        g = delegating_gen(results, k)
        next(g)
        for val in values:
            g.send(val)
        g.send(None) # ommit this line will result {}. don't exactly know what happened:w
    print(results)

def delegating_gen(results, key):
    while True:
        # !!! this is data passing to sub_gen w/ yield from
        # where's inputs for sub_gen() ???
        #   not here : inputs come from caller's send : g.send(val)
        #   this is just acts as a channel
        results[key] = yield from sub_gen()

def sub_gen(): # simple averager
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield
        if term is None:
            break
        total += term
        count += 1
        average = total / count
    return Result(count, average)

""" 
sample run
get multiple list's average in one pass
>>> d = {'a':[1, 2, 3], 'b':[4, 5, 6]}
>>> caller(d)
{'b': Result(count=3, average=5.0), 'a': Result(count=3, average=2.0)}
"""
