import asyncio
import itertools
import sys


async def spin(msg):
    print('start spin')
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))
        try:
            await asyncio.sleep(.1)
        except asyncio.CancelledError:
            break
    write(' ' * len(status) + '\x08' * len(status))


async def slow_function():
    await asyncio.sleep(3)
    return 42


async def supervisor():
    # runs spin coroutine as task
    spinner = asyncio.ensure_future(spin('thinking'))
    print('spinner object:', spinner)
    result = await slow_function()
    spinner.cancel()  # spin 코루틴은 cancelException에 멈추게 되어 있다
    return result


def main():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(supervisor())
    loop.close()
    print('Answer:', result)


if __name__ == '__main__':
    main()
