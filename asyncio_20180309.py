import asyncio


# ====================================================
# 궁금한 점들
#   - coroutine, future, task 차이점
#   - 각각을 실행하는 방법들 : 간단한 것부터 고급 내용까지
#   - 일반함수와 혼용하기

# ====================================================
# ====================================================
# fluent python ch16
#   - concepts
#     - generator
#       - function has yield x
#       - return value to caller through next(gen)
#     - coroutine
#       - function has x = yield
#       - usually gets value from caller through coro.send(val)
#     - yield
#       - just a control flow device
#       - don't care it gets or returns values
# ----------------------------------------------------
# ----------------------------------------------------


# ====================================================
# coroutine w/ generator
# ----------------------------------------------------
def test_gen_coro():
    def gen_coro():
        print('before priming')
        x = yield
        print(x)

    gc = gen_coro()
    print(gc)

    try:
        next(gc)
        gc.send(10)
    except StopIteration as e:
        pass


# ====================================================
# native coroutine
#   - native coroutine은 다른 native coroutine 안에서만 호출 될 수 있다.
#   - await coro 형태로 호출한다.
#   - 최초 native coroutine은 누가 호출? -> eventloop 에서 한다.
# ----------------------------------------------------
async def test_async_coro():
    async def async_coro():
        print('befor priming')
        #  - generator coroutine 과 같이 값을 전달하는 형태는 만들수 없는가보다
        #    - await x 와 같이 yield x 를 대체할 문법은 없다.
        #    - await는 다른 coroutine을 호출할 때 사용한다.
        # await x  # errcode
        # print(x)  # errcode

    ac = async_coro()
    print(ac)
    print(await ac)


# ====================================================
# coroutine
#   - create coroutine by putting 'async' in front of def
#   - only coroutine function can use 'await'
#   - call coroutine function returns coroutine object
# ----------------------------------------------------
def test_coroutine():
    # define coroutine function
    async def sample_coro_func():
        return 10
        # print('coro func')

    coro_obj = sample_coro_func()
    # print(await coro_obj)
    # print(asyncio.ensure_future(coro_obj))
    asyncio.ensure_future(coro_obj)


def test_sleep():
    print('before')
    # await asyncio.sleep(10)
    print('after')


if __name__ == '__main__':
    print('test start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    # test_coroutine()
    # test_sleep()
    test_gen_coro()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_async_coro())
