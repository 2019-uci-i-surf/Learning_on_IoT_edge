# import the necessary packages

from settings import *
from multiprocessing import Process
from cameraclient import CameraClient

PORT = 10001

if __name__ == '__main__':
    procs = list()
    for process_number in range(2):
        proc = Process(target=CameraClient.mp_routine, args=(SERVER_HOST, PORT))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()
