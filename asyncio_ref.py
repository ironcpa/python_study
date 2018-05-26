import asyncio
from pprint import pprint
import random
import time
from datetime import datetime
import functools
from threading import Thread
import logging
import aiohttp


# =============================================================================
# 여기에 asyncio 사용법의 모든 것을 정리해 본다.
# asyncio 는 결국 coroutine 실행을 위한 것으로 보인다.
# 하지만 호출하는 방식과 loop를 다루는 함수가 다양하고 예제마다 사용 방식이 다르다.
# 보이는 대로 여기에, 새로운 것은 추가하고 유사한 것은 정리/분류 하여 레퍼런스로 만든다.
# =============================================================================

# -----------------------------------------------------------------------------
# event loop 이해
#   - loop에서 task/future/coroutine 이 실행된다.
#   - task/future 안에는 coroutine이 있으므로 실행단위는 코루틴으로 보면 된다.
#     - 예에서는 task를 만드는 과정들이 들어가지만
#     - 라이브러리들이 async 함수를 지원하면 그대로 호출하면 된다.
#     - 아직은 async 함수를 지원하는 라이브러리가 별로 없다.
#   - 하나의 코루틴이 await을 만나면 다른 병렬적인 코루틴이 실행된다.
#   - chaining된 경우는 순차적으로 실행된다. - chainging 참조
# event loop 생성 및 디폴트 루프?
#   - 현재 쓰레드의 이벤트루프 얻기: asyncio.get_event_loop(), 메인 쓰레드에서만 사용
#     - 메인 쓰레드에는 이미 설정된 루프가 있다는 의미
#     - 다른 쓰레드에는 set_event_loop()로 설정 해야함
#   - 디폴트 루프: 현재 쓰레드의 루프, api 중 루프 전달이 선택적인 경우 이걸 사용
def test_event_loop():
    async def coro_1():
        print('start of coro 1 with context')
        print('context switch to coro 2')
        await asyncio.sleep(0)
        print('coro 1 gets context')

    async def coro_2():
        print('coro 2 gets context')
        await asyncio.sleep(0)
        print('content switch back to coro 1')

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(coro_1()),
             loop.create_task(coro_2())]
    loop.run_until_complete(asyncio.wait(tasks))
    print('end of main')


# -----------------------------------------------------------------------------
# src: https://medium.freecodecamp.org/a-guide-to-asynchronous-programming-in-python-with-asyncio-232e2afa44f6
# sleep을 예로들어 비동기 코루틴 호출 원리 이해
#   - custom_sleep 에서
#     - time.sleep 사용 버전과
#     - asyncio.sleep 사용 버전을 비교 실행 시 시간 차이를 확인할 수 있다.
#   - 결과분석
#     - 실행 시간이 async 버전이 2초 가량 빠르다.
#     - async 버전에서는 sleep 발생 시 스위칭이 발생하여 놀지 않는다.
def test_sleep():
    async def custom_sleep():
        print('sleep', datetime.now())
        # time.sleep(1)
        await asyncio.sleep(1)

    async def factorial(name, number):
        f = 1
        for i in range(2, number+1):
            print('task {}: compute factorial({})'.format(name, i))
            await custom_sleep()
            f *= i
        print('task {}: factorial({}) is {}\n'.format(name, number, f))

    start = time.time()
    loop = asyncio.get_event_loop()

    tasks = [
        asyncio.ensure_future(factorial('A', 3)),
        asyncio.ensure_future(factorial('B', 4)),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    end = time.time()
    print('total time: {}'.format(end - start))


# -----------------------------------------------------------------------------
# future와 task
# - task는 future의 구현이므로 loop에 예약걸 때는 유사하게 보면 된다.
# - task는 생성 시 loop에 스케쥴링 된다.
# - await 없이 만들면 독립적으로 스케쥴링 된다.
# - await 에 이어 나올 경우 해당 task 종료시까지 다른 task들이 대기한다.

# -----------------------------------------------------------------------------
# task나 future 만들기 함수들
# 이 함수들은 어떤 용도인가?
# - 함수들
#   - create_task
#     - coroutine을 받음
#     - task 리턴
#     - loop 컨텍스트에서 호출됨?
#   - ensure_future
#     - future, coroutine, awaitable objects를 받음
#     - task 리턴, future 받은 경우 future 리턴
#     - coroutine 받은 경우 create_task 사용
#     - 선택적으로 loop 전달 가능
# - 문법
#   - async def
#     - coroutine 생성 함수

# -----------------------------------------------------------------------------
# asyncio를 통한 코루틴 실행 방법은 아래 2가지를 알아야 한다.
# 하나는 코루틴 실행 함수들이고, 다른 하나는 loop에 코루틴을 탑재하는 scheduler 함수이다.
# 코루틴 실행 함수 호출 시 미래에 실행이 예약되게 된다.
# 물론 loop 탑재 해야 루프 안에서 실행된다.
# - 코루틴 실행 함수들
#   - gather
#   - wait
#   - ...
# - loop 실행 함수들: 다양한 실행 방법이 준비되어 있음
#   - run_forever: until stop() called
#   - run_until_complete: until future is done
#     - 코루틴이 직접 전달되면 ensure_future()로 감싼다
#   - ...
async def coro(tag):
    print('>', tag)
    await asyncio.sleep(random.uniform(1, 3))
    print('<', tag)
    return tag

# -----------------------------------------------------------------------------
# 코루틴을 직접 스케쥴링 함수에 전달
#   별다른 절차 없이 async def 로 정의된 코루틴을 그대로 전달 가능하다.
def test_direct_coroutine():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coro('simple'))
    loop.close()

# -----------------------------------------------------------------------------
# future 직접 만들기
#   Future 객체를 직접 만들 수 있지만 여기서는 loop로 만드는 방법을 설명한다.
#   loop.create_future() 로 생성한다.
#   실행 로직이 없는 상태만 가진 객체이다.
#     - await 걸거나 loop에 스케쥴링 하면 실행 상태가 되고
#     - set_result() 받으면 종료된다.
def test_create_future():
    async def coro(future):
        print('inside coro')
        # 아래 라인이 없다면 future는 await 상태에서 종료되지 않고 멈춰있다.
        future.set_result(999)

    loop = asyncio.get_event_loop()
    f = loop.create_future()
    c = coro(f)
    tasks = [f, c]
    done, pending = loop.run_until_complete(asyncio.wait(tasks))
    for t in done:
        print(t.result())
    print('end of main')


# -----------------------------------------------------------------------------
# gather
#   n개 코루틴들의 실행 결과를 모든다.
#   gather 그룹에 대한 gather 그룹을 중첩으로 만들 수 있는 장점이 있다.
#     - 아래 예에서 all_groups
def test_gather():
    loop = asyncio.get_event_loop()

    group1 = asyncio.gather(*[coro('group 1.{}'.format(i)) for i in range(1, 6)])
    group2 = asyncio.gather(*[coro('group 2.{}'.format(i)) for i in range(1, 4)])
    group3 = asyncio.gather(*[coro('group 3.{}'.format(i)) for i in range(1, 10)])

    all_groups = asyncio.gather(group1, group2, group3)
    print('who am i?', all_groups)

    # results = loop.run_until_complete(group1)
    results = loop.run_until_complete(all_groups)

    loop.close()

    pprint(results)


# -----------------------------------------------------------------------------
# wait
#   return_when 조건을 주어 단계적 실행이 가능하다.
def test_wait():
    loop = asyncio.get_event_loop()

    tasks = [coro(i) for i in range(1, 11)]

    print('get first result:')
    finished, unfinished = loop.run_until_complete(
        asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    )

    for task in finished:
        print(task.result())
    print('unfinished:', len(unfinished))

    print('get more results in 2 seconds:')
    finished2, unfinished2 = loop.run_until_complete(
        asyncio.wait(unfinished, timeout=2)
    )

    for task in finished2:
        print(task.result())
    print('unfinished2:', len(unfinished2))

    print('get all other results:')
    finished3, unfinished3 = loop.run_until_complete(
        asyncio.wait(unfinished2)
    )

    for task in finished3:
        print(task.result())

    loop.close()

# -----------------------------------------------------------------------------
# async def 요건
#   - await가 없어도 된다.
#   - await 가 2회 이상 발생할 수 있다.

# -----------------------------------------------------------------------------
# ensure_future는 구분안에 들어있기만 해도 loop에서 호출된다.
#   - 아래 예를 보면 coro_sub가 호출되는 것을 볼 수 있다.
#   - 그러므로 ensure_future는 자체로 호출 함수임을 의미한다.
#   - fluent python 에서도 asyncio.async(), loop.create_task() 호출 순간 스케쥴링 된다고 언급한다.
def test_simplest_run_coro():
    async def coro(msg):
        print('simple coro', msg)
        await asyncio.sleep(.1)
        sub_coro = asyncio.ensure_future(coro_sub(msg))
        # sub_coro.cancel()  # 이렇게 바로 cancel 하면 실행되지 않음을 볼 수 있다
                             # 반면 cancel 안하면 pending 예외가 뜬다
                             # 결국 이 방법은 가능하긴 하지만 관리 안되는 방법인가?

    async def coro_sub(msg):
        print("i'm sub coro", msg)
        await asyncio.sleep(.1)

    simple_coro = coro('xxx')
    print(simple_coro)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(simple_coro)  # coroutine을 직접 받을 수 있다.
    # loop.run_until_complete(loop.create_task(simple_coro))  # task로도 받을 수 있다.
    # ----------------------------------------------
    # 아래 방법은 pending된 coro_sub를 처리하려는 노력
    #   - 하지만 pending 결과에는 coro_sub가 들어있지 않음
    #   - 결국 관리 안되는 것이 맞는 듯
    # ----------------------------------------------
    # futures = [asyncio.ensure_future(simple_coro)]
    # done, pending = loop.run_until_complete(asyncio.wait(futures))
    # print('done:', done)
    # print('pending:', pending)
    # if pending:
    #     for task in pending:
    #         task.cancel()

    loop.close()

# -----------------------------------------------------------------------------
# 일반 함수를 콜백으로 사용
#   event loop는 콜백을 스케쥴링 하고 호출 할 수 있다.
#   loop에서 실행하기 위해서는 드라이버 역할의 코루틴을 만들긴 해야 한다. - 예에서 main()
def test_normal_func_as_callback():
    def callback(arg, *, kwarg='default'):
        print('callback: {}, {}'.format(arg, kwarg))

    async def main(loop):
        print('registering callbacks')
        loop.call_soon(callback, 1)
        wrapped = functools.partial(callback, kwarg='not default')
        loop.call_soon(wrapped, 2)

        await asyncio.sleep(.1)

    loop = asyncio.get_event_loop()
    try:
        print('run loop')
        loop.run_until_complete(main(loop))
    finally:
        print('close loop')
        loop.close()

# loop에서 blocking 함수 호출
#   run_in_executor
#     - 내부적으로 thread로 실행된다고 보면 된다. 디폴트로 ThreadPoolExecutor 사용

# Future object on event loop's run_until_complete
def test_future():
    async def slow_operation(future):
        await asyncio.sleep(1)
        future.set_result('future is done')

    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    asyncio.ensure_future(slow_operation(future))
    loop.run_until_complete(future)  # toss future!
    # 아래 처럼 해도 동일한 결고를 얻는다
    # ----------------------------
    # a = asyncio.ensure_future(slow_operation(future))
    # loop.run_until_complete(a)
    print('future.result:', future.result())
    loop.close()

# Future object on event loop's run_forever
def test_future_in_run_forever():
    async def slow_operation(future):
        await asyncio.sleep(1)
        future.set_result('future is done')

    def got_result(future):
        print('inside callback', future)
        print(future.result())
        print('inside callback:', loop)
        loop.stop()

    loop = asyncio.get_event_loop()
    print('check loop:', loop)
    future = asyncio.Future()
    asyncio.ensure_future(slow_operation(future))
    future.add_done_callback(got_result)
    try:
        loop.run_forever()
    finally:
        loop.close()

# -----------------------------------------------------------------------------
# Task: Future 의 subclass, coroutine을 실행할 future로 보면 됨
#   보통 직접 생성하지 않고 2가지 방법으로 만든다.
#     - asyncio.ensure_future()
#     - loop.create_task()
#   관련 함수
#     - asyncio.as_completed(): 코루틴들을 받아서 끝나는 순서대로 리턴?
#                               for문과 같이 쓴다. await 와 같이 쓸 수 없었다.
#     - asyncio.ensure_future(): 코루틴들을 받아서 task로 만듬
#                                loop.create_task() 와 같음
#     - asyncio.gather(): 코루틴들을 실행 후 전체 결과를 모아서 리턴
#                         결과 순서는 원래 코루틴 순서대로 정렬됨
#     - asyncio.sleep(): 지정 시간 소모하는 코루틴 생성
#     - asyncio.wait_for(): 1개 코루틴 받아 실행
#     - asyncio.wait(): 코루틴들을 받아 단계적 실행, 다른 함수보다 원시적
#                       하나만 완료될 때까지 실행할 지, 모두 완료까지 기다릴 지 지정 가능
#                       단계적 실행 등 미세 컨트롤 가능
def test_varying_coro_run():
    async def coro(msg):
        await asyncio.sleep(1)
        print('coro({}) completed'.format(msg))
        return 'coro result: ' + msg

    loop = asyncio.get_event_loop()

    # wait_for
    co = coro('111')  # coruotine object
    r = loop.run_until_complete(asyncio.wait_for(co, 3))
    print(r)

    # wait
    co_list = [coro('222'),
               coro('333')]
    finished, unfinished = loop.run_until_complete(asyncio.wait(co_list))
    for task in finished:
        print(task.result())

    # as_completed
    async def drive_as_completed():
        co_list = [coro('444'),
                   coro('555')]
        # runs = asyncio.as_completed(co_list)
        # print(runs)
        for task in asyncio.as_completed(co_list):
            r = await task
            print(r)
    loop.run_until_complete(drive_as_completed())


# -----------------------------------------------------------------------------
# asyncio 개발 시 주의 사항
#   - debug 옵션: loop.set_debug(True) 로 상세 진단 가능
def test_debugging():
    def normal(msg, loop):
        print('inside normal:', msg)
        loop.stop()

    async def coro(msg, loop):
        #await asyncio.sleep(.5)
        print('inside coro:', msg)
        loop.stop()

    loop = asyncio.get_event_loop()
    # set_debug: 자세한 trace 표시
    loop.set_debug(True)
    #loop.call_soon(normal, 'aaa', loop)
    loop.call_soon(coro, 'aaa', loop)
    loop.run_forever()
    print('end of test')

#   - cancel 방법
#     - future/task는 명시적 cancel 필요하다.
#     - wait_for()는 timeout 후 자동 cancel 된다.
#     - cancel된 경우 set_result(), set_exception() 호출하지 마라.
#       - cancelled() 로 체크 후 호출하라.
#       - loop.call_soon() 호출 후 호출하면 안된다. 이미 cancel 되었을 수 있다.
def test_cancel():
    async def fast_logic(msg, slow_job):
        await asyncio.sleep(1)
        if not slow_job.done() and not slow_job.cancelled():
            #slow_job.set_result('injected result')
            slow_job.cancel()
        print('insize fast_logic:', msg)
        return 'default result'

    async def slow_logic(msg):
        await asyncio.sleep(5)
        #await asyncio.sleep(.5)
        print('inside slow_logic:', msg)
        return 'default result'

    slow_fut = asyncio.ensure_future(slow_logic('bbb'))
    fast_fut = asyncio.ensure_future(fast_logic('aaa', slow_fut))

    loop = asyncio.get_event_loop()

    finished, _ = loop.run_until_complete(asyncio.wait([fast_fut, slow_fut]))
    print('end of main thread:')
    for task in finished:
        print(task.result())


#   - 별도 thread에서 loop 실행 시 주의사항
#     - loop.call_soon_threadsafe() 와 같이 멀티쓰레드용 함수를 써야 한다.
#       - 일반함수용: loop.call_soon_threadsafe()
#       - 코루틴용: loop.run_coroutine_threadsafe()
def test_loop_w_threads():
    def normal(loop):
        time.sleep(2)
        print('inside normal')
        loop.stop()

    def driver(loop):
        print('inside driver')
        loop.call_soon_threadsafe(normal, loop)
        loop.run_forever()

    loop = asyncio.get_event_loop()

    t = Thread(target=normal, args=(loop,))
    t.start()
    print('end of main')


#   - blocking function: loop.run_in_executor()
#   - logging: logging 모듈의 'asyncio' 로거에서 확인 가능
def test_asyncio_log():
    async def coro():
        await asyncio.sleep(.5)
        print('inside coro')
        logging.error('>>>>>> some log')

    logging.getLogger('asyncio').setLevel(logging.WARNING)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coro())
    print('end of main')


#   - 스케쥴 안 된 코루틴 식별: 실행 시 runtime warning을 발생한다.
#     - 코루틴은 반드시 ensure_future, create_task 등의 방법으로 실행 스케쥴링 해야한다.
def test_detect_unscheduled_coro():
    async def coro():
        print('inside coro')

    coro()


#   - 잡지 못한 예외가 있으면 loop 진행되지 못하고 멈춘다.
#     - debug 모드 켜고 원인을 확인 할 수 있다.
def test_unconsumed_exception():
    async def coro():
        print('inside coro')
        raise Exception('not consumed')

    loop = asyncio.get_event_loop()
    #loop.set_debug(True)  # debug 모드 켜면 자세한 정보 확인 가능
    asyncio.ensure_future(coro())
    loop.run_forever()
    print('right after loop run')  # 예외로 인해 여기 도달 못한다.
    loop.close()
    print('end of main')


#     - 조치 방법
#       - 예외 처리용 코루틴을 연결하여 처리
def test_handle_exception_w_handler_coro():
    async def coro(loop):
        print('inside coro')
        raise Exception('not consumed')
        loop.stop()

    async def handle_exception(loop):
        try:
            await coro(loop)
        except Exception:
            print('catch exception')
            loop.stop()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(handle_exception(loop))
    loop.run_forever()
    loop.close()
    print('end of main')


#       - run_until_complete() 의 경우 예외가 전파된다.
def test_handle_exception_w_run_until_complete():
    async def coro(msg, throw_exp):
        print('inside coro:', msg)
        if throw_exp:
            raise Exception('not consumed')

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(asyncio.ensure_future(coro('aaa', True)))
    except Exception as e:
        print('catch exception:', e)


#         - multi task 에 대해서는 결과 처리에서 예외를 잡아야 한다.
def test_handle_exception_w_run_until_complete_multi_coro():
    async def coro(msg, throw_exp):
        print('inside coro:', msg)
        if throw_exp:
            raise Exception('not consumed')
        return 'result:', msg

    loop = asyncio.get_event_loop()

    futures = [asyncio.ensure_future(coro('aaa', True)),
               asyncio.ensure_future(coro('bbb', False)),
               asyncio.ensure_future(coro('ccc', False))]

    done, _ = loop.run_until_complete(asyncio.wait(futures))
    pprint(done)
    print('done:', len(done))
    for t in done:
        try:
            print(t.result())
        except Exception as e:
            print('catch exception:', e)


#   - 코루틴에서 코루틴 호출하기 방법
def test_call_coroutine_in_coroutine():
    async def coro_4_task(msg):
        print('inside task:', msg)

#     - 직접 await 호출: chaining
    async def coro1():
        print('1-----------------')
        await coro_4_task('<-1')  # coro1 전에 예약됨
        print('inside coro1')

#     - 따로 task로 만들기: task는 예약을 건다!
    async def coro2():
        print('2-----------------')
        # loop 에 싣지 않아도 실행이 된다!
        asyncio.ensure_future(coro_4_task('<-2'))  # coro2 보다 늦게 예약 처리
        print('inside coro2')

#     - await task: chaining, 직접 await 호출과 같다
    async def coro3():
        print('3-----------------')
        # 정확히는 coro2 보다 아래와 같이 하는게 명확하다.
        await asyncio.ensure_future(coro_4_task('<-3'))  # coro2 보다 늦게 예약 처리
        print('inside coro3')

    loop = asyncio.get_event_loop()
    futures = [coro1(), coro2(), coro3()]
    loop.run_until_complete(asyncio.wait(futures))
    print('end of main')


#   - 단순히 task 만들어 예약거는 경우 모든 task 실행 전에 loop.close() 될 수 있다.
def test_coroutine_chaining():
    async def create():
        await asyncio.sleep(3.0)
        print('(1) create file')

    async def write():
        await asyncio.sleep(1,0)
        print('(2) write into file')

    async def close():
        print('(3) close file')

    # 순서 보장이 안됨: 병렬 실행
    #   - 이 코루틴은 순서대로 실행되지도 않고
    #   - (1)은 pending 상태로 loop.close() 된다.
    #   - job_ok1, job_ok2 처럼 해야 의도대로 실행된다.
    async def job():
        asyncio.ensure_future(create())
        asyncio.ensure_future(write())
        asyncio.ensure_future(close())
        await asyncio.sleep(2.0)
        loop.stop()

    # 적절한 chaining
    async def job_ok1():
        await asyncio.ensure_future(create())
        await asyncio.ensure_future(write())
        await asyncio.ensure_future(close())
        await asyncio.sleep(2.0)
        loop.stop()

    # 적절한 chaining
    async def job_ok2():
        await create()
        await write()
        await close()
        await asyncio.sleep(2.0)
        loop.stop()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(job())
    #asyncio.ensure_future(job_ok1())
    #asyncio.ensure_future(job_ok2())
    loop.run_forever()
    print('pending tasks at exit: {}'.format(asyncio.Task.all_tasks(loop)))
    loop.close()


# -----------------------------------------------------------------------------
# async/await hell
# - await chain에 의해 실행 순서가 복잡해 지거나 쓸데 없이 다른 코루틴에 의존하여 느려지는 문제들
# - callback hell을 빠져 나왔더니 마주하는 새로운 문제로 부각
# - 코루틴 chaining을 어떻게 구성할지 고민해야 하는 이유
# - this example is from :
#   - https://medium.freecodecamp.org/avoiding-the-async-await-hell-c77a0fb71c4c
#   - javascript example
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

pizza_data = None
drink_data = None
shopping_cart = ShoppingCart()
def test_await_hell():
    class Pizza:
        def __init__(self, name, price):
            self.name = name
            self.price = price

        def __repr__(self):
            return '{}={}'.format(self.name, self.price)

    class Drink:
        def __init__(self, name, price):
            self.name = name
            self.price = price

        def __repr__(self):
            return '{}={}'.format(self.name, self.price)

    async def get_pizza_data():
        await asyncio.sleep(3)
        print('get pizza data')
        return {'plane': Pizza('plane', 100),
                'pepperoni': Pizza('pepperoni', 150)}

    async def get_drink_data():
        await asyncio.sleep(2)
        print('get drink data')
        return {'water': Drink('water', 10),
                'soda': Drink('soda', 20),
                'coke': Drink('coke', 30)}

    def choose_pizza(name):
        pizza = pizza_data[name]
        print('choose pizza:', pizza)
        return 'pizza({})'.format(pizza)

    def choose_drink(name):
        drink = drink_data[name]
        print('choose drink:', drink)
        return 'drink({})'.format(drink)

    async def add_pizza_to_cart(pizza):
        print('cart: pizza {} added'.format(pizza))
        shopping_cart.add(pizza)

    async def add_drink_to_cart(drink):
        print('cart: drink {} added'.format(drink))
        shopping_cart.add(drink)

    async def get_cart_items():
        print('get cart items')
        return shopping_cart.items

    async def send_order_request(item):
        print('order {}'.format(item))

    # async/await hell: slow way order
    async def order_items():
        items = await get_cart_items()
        for item in items:
            await send_order_request(item)

    async def order_items_wo_hell():
        items = await get_cart_items()
        tasks = [send_order_request(i) for i in items]
        # 아래 방법은 안된다.
        #   - tasks의 코루틴들이 never awaited 로 경고 발생한다.
        #   - gather 처럼 await 을 붙여도 안된다.
        #     - as_completed는 generator를 리턴하기 때문, for loop에 특화된 용법
        #asyncio.as_completed(tasks)
        #await asyncio.as_completed(tasks)
        for t in asyncio.as_completed(tasks):
            print(t)

    # async/await hell: slow way
    async def job_w_hell():
        global pizza_data, drink_data
        pizza_data = await get_pizza_data()
        drink_data = await get_drink_data()
        pizza = choose_pizza('pepperoni')
        drink = choose_drink('coke')
        await add_pizza_to_cart(pizza)
        await add_drink_to_cart(drink)
        await order_items()

    async def select_pizza():
        global pizza_data
        pizza_data = await get_pizza_data()
        pizza = choose_pizza('pepperoni')
        await add_pizza_to_cart(pizza)

    async def select_drink():
        global drink_data
        drink_data = await get_drink_data()
        drink = choose_drink('coke')
        await add_drink_to_cart(drink)

    async def job_wo_hell():
        await asyncio.gather(*[select_pizza(), select_drink()])
        #await order_items()
        await order_items_wo_hell()

    loop = asyncio.get_event_loop()
    #loop.run_until_complete(job_w_hell())
    loop.run_until_complete(job_wo_hell())
    print('end of main')

# -----------------------------------------------------------------------------
# aiohttp
#   - client: 비동기 처리로 빨라지긴 하지만 blocking 처리 관련 api가 느려 효과가 별로다.
#             아래 2가지 설치하면 빨라진다.
#     - dns resolve: aiodns 설치하면 빨라진다.
#     - chardet: cchardet 설치하면 빨라진다.
def test_aiohttp_client():
    async def fetch(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                html = await res.text()
                print(html)

    loop = asyncio.get_event_loop()

    tasks = [fetch('http://python.org'),
             fetch('http://si.com')]
    loop.run_until_complete(asyncio.wait(tasks))


def test_aiohttp_server():
    from aiohttp import web
    async def handle(req):
        name = req.match_info.get('name', 'Anonymous')
        text = 'hello, ' + name
        return web.Response(text=text)

    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.get('/{name}', handle)])

    web.run_app(app)


def test_subprocess():
    import sys
    print(sys.platform)
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    print(loop)

    async def run_command(*args):
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE
        )

        print('started:', args, '(pid=' + str(process.pid) + ')')
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print('done:', args, '(pid=' + str(process.pid) + ')')
        else:
            print('failed:', args, '(pid=' + str(process.pid) + ')')

        result = stdout.decode().strip()

        return result

    async def run_command_shell(command):
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE
        )

        print('started:', command, '(pid=' + str(process.pid) + ')')
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print('done:', command, '(pid=' + str(process.pid) + ')')
        else:
            print('failed:', command, '(pid=' + str(process.pid) + ')')

        result = stdout.decode().strip()

        return result

    def make_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def run_asyncio_commands(tasks, max_concurrent_tasks=0):
        all_results = []

        if max_concurrent_tasks == 0:
            chunks = [tasks]
        else:
            chunks = make_chunks(l=tasks, n=max_concurrent_tasks)

        for tasks_in_chunk in chunks:
            if sys.platform == 'windows':
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
            else:
                loop = asyncio.get_event_loop()

            commands = asyncio.gather(*tasks_in_chunk)
            results = loop.run_until_complete(commands)
            all_results += results
            loop.close()

        return all_results

    start = time.time()

    '''
    commands = [
        ['ls', '-l', '/home/hjchoi'],
        ['hostname'],
    ]
    tasks = [run_command(*cmd) for cmd in commands]
    '''
    commands = [
        'ls -l /home/hjchoi',
        'hostname'
    ]
    tasks = [run_command_shell(cmd) for cmd in commands]

    results = run_asyncio_commands(tasks, max_concurrent_tasks=20)
    print('results:', results)

    end = time.time()
    rounded_end = ('{0:.4f}'.format(round(end - start, 4)))
    print('script ran in about', str(rounded_end), 'seconds')


if __name__ == '__main__':
    #test_event_loop()
    #test_sleep()
    #test_direct_coroutine()
    #test_create_future()
    #test_gather()
    #test_wait()
    #test_simplest_run_coro()
    #test_normal_func_as_callback()
    #test_future()
    #test_future_in_run_forever()
    #test_varying_coro_run()
    #test_debugging()
    #test_cancel()
    #test_loop_w_threads()
    #test_asyncio_log()
    #test_detect_unscheduled_coro()
    #test_unconsumed_exception()
    #test_handle_exception_w_handler_coro()
    #test_handle_exception_w_run_until_complete()
    #test_handle_exception_w_run_until_complete_multi_coro()
    #test_call_coroutine_in_coroutine()
    #test_coroutine_chaining()
    #test_await_hell()
    #test_aiohttp_client()
    #test_aiohttp_server()
    test_subprocess()
