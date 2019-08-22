# import the necessary packages

from settings import *
from multiprocessing import Process
from cameraclient import CameraClient

if __name__ == '__main__':
    procs = list()
    for process_number in range(1):
        proc = Process(target=CameraClient.mp_routine, args=(SERVER_HOST, SERVER_PORT))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()
