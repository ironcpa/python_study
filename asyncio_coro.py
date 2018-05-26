# native 코루틴에 대해 알아본다.
# - async def 로 정의된 함수는 native coroutine 이다.
# - python에는 2가지 코루틴이 있다
#     1. native coroutine : async def
#     2. generator based coroutine : using yield keyword
#
# await keyword can be used only in native coroutines
#
# 아래에서 몇가지 테스트를 해 봤는데
# 역시 아직 정확한 건 이해가 되지 않는다.
# native 코루틴은 loop와 함께 구조적인 부속으로 쓰이는 듯 하다.

import asyncio


# this is simple coroutine
async def hello(name):
    print('hello, world!', name)

# simple way to run coroutine w/ event loop
'''
loop = asyncio.get_event_loop()
loop.run_until_complete(hello('aaa'))
loop.close()
'''


'''
>>> c = hello('ccc')
>>> c.send(None)
hello, world! ccc
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
'''

# Diff vs generator coroutine >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# 개인적인 native coroutine과 generator coroutine 궁금점을 풀어본다.
# can't make averager coroutine example in generator_coro.py
# can't use yield in python 3.5, 3.6 supports it
# below code fails on 'yield average' line
# this test file's scope is bit broader than that
from collections import namedtuple
Result = namedtuple('Result', 'count average')
async def averager():
    """averager w/ native coroutine"""
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
    #return Result(count, average)  # can't return value in async_generator


# try to understand async_generator
import pdb
# using async_generator
async def xrange(numbers):
    for i in range(numbers):
        pdb.set_trace()
        yield i
        #await asyncio.sleep(0)

async def coroutine_wrapper(async_gen, args):
    try:
        print(tuple([i async for i in async_gen(args)]))
    except ValueError:
        print(tuple([(i, j) async for i, j in async_gen(args)]))

def using_async_gen():
    print('begin loop>>>>>>>>>>>>>>>>')
    #loop = asyncio.get_event_loop()  # get_event_loop() gets 'current' loop
    loop = asyncio.new_event_loop()
    xrange_iterator_task = loop.create_task(coroutine_wrapper(xrange, 20))
    try:
        loop.run_until_complete(xrange_iterator_task)
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()
    print('<<<<<<<<<<<<<<<<<<end loop')
    print()
    print('type(xrange) == {}'.format(type(xrange)))
    print('type(xrange(20)) == {}'.format(type(xrange(20))))
    print()
    print('type(coroutine_wrapper) == {}'.format(type(coroutine_wrapper)))
    print('type(coroutine_wrapper(xrange,20))'.format(type(coroutine_wrapper(xrange, 20))))

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


"""
await 키워드
 - yield from 대신 사용한다. yield 대신이 아니다.
 - native coroutine 안에서만 사용한다
 - 아래와 같은 객체 앞에 사용한다. 일반 값에 사용하는게 아니다. 
 - 의미는 코루틴/퓨처/테스크를 호출한다고 보면 된다.
   변수 = await 코루틴객체
   변수 = await 퓨처객체
   변수 = await 테스크객체
"""

# simple application

import asyncio

async def add(a, b):
    print('add: {0} * {1}'.format(a, b))
    await asyncio.sleep(1.0)
    return a + b

async def print_add(a, b):
    result = await add(a, b)
    print('print_add: {0} + {1} = {2}'.format(a, b, result))

def simple_application1():
    '''
    >>> loop = asyncio.new_event_loop()
    >>> loop.run_until_complete(print_add(1, 2))
    add: 1 * 2
    print_add: 1 + 2 = 3
    >>> loop.close()
    '''
    pass

'''>> sample web download >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
things to note
 - loop.run_in_executor : call sync function in native coroutine
'''
def web_download_simple():
    from time import time
    from urllib.request import Request, urlopen

    urls = ['https://www.google.co.kr/search?q=' + i
            for i in ['apple', 'pear', 'grape', 'pineapple', 'orange', 'strawberry']]

    begin = time()
    result = []
    for url in urls:
        request = Request(url, headers={'User-Agent': 'Mozilla/5.8'})
        response = urlopen(request)
        page = response.read()
        result.append(len(page))

    print(result)
    end = time()
    print('실행 시간: {0:.3f}초'.format(end - begin))

def web_download_async():
    from time import time
    from urllib.request import Request, urlopen
    import asyncio

    urls = ['https://www.google.co.kr/search?q=' + i
            for i in ['apple', 'pear', 'grape', 'pineapple', 'orange', 'strawberry']]

    async def fetch(url):
        request = Request(url, headers={'User-Agent': 'Mozilla/5.8'})
        # call sync function in native coroutine : run_in_executor()
        #  - 1st arg None is executor : thread pool to execute sync function
        response = await loop.run_in_executor(None, urlopen, request)
        page = await loop.run_in_executor(None, response.read)
        return len(page)

    # function that gather results from multiple futures
    # need wrapper function to wrap futures
    async def future_wrapper():
        # ensure_future : makes corutines as task
        futures = [asyncio.ensure_future(fetch(url)) for url in urls]
        result = await asyncio.gather(*futures)
        print(result)

    begin = time()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(future_wrapper())
    loop.close()
    end = time()
    print('실행 시간: {0:.3f}초'.format(end - begin))
'''<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'''

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose = True)
    #simple_application1()
