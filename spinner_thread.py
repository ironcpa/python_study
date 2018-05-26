import sys
import itertools
import time
import threading

class Signal:
    # go is a signal attribute to go or stop
    #   - default w/ true
    #   - change false if you want to stop a job
    go = True


def spin(msg, signal):
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))  # this doen't work in pycharm run output
        time.sleep(.1)
        if not signal.go:
            break
    write(' ' * len(status) + '\x08' * len(status))


def slow_function():
    # pretend long time job for I/O
    time.sleep(3)
    return 42


def supervisor():
    signal = Signal()
    spinner = threading.Thread(target=spin,
                               args=('thinking!', signal))
    spinner.start()  # start thread: means show spinner
    result = slow_function()
    signal.go = False  # send signal to thread to stop
                       #   change go to false right after slow job
    spinner.join()  # main thread holding until sippiner thread end
    return result


def main():
    result = supervisor()
    print('Answer:', result)


if __name__ == '__main__':
    main()