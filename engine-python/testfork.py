import time
import os


def main():
    child_pid = os.fork()
    if child_pid == 0:
        parent_id = os.getppid()
        while True:
            if os.getppid() == 1:
                print('child exit', os.getppid(), parent_id)
                break
            time.sleep(1)
    else:
        time.sleep(2)
        print('parent exit')


if __name__ == '__main__':
    main()
