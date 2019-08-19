from server1 import ProcessingServer
from settings import *
from multiprocessing import Process

if __name__ == '__main__':
    client1 = ProcessingServer(SERVER_HOST, 10001)
    client2 = ProcessingServer(SERVER_HOST, 10002)
    client3 = ProcessingServer(SERVER_HOST, 10003)
    client4 = ProcessingServer(SERVER_HOST, 10004)

    client1.run_task1(WEIGHT_PATH, CLASS_NAMES)
    client2.run_task1(WEIGHT_PATH, CLASS_NAMES)
    client3.run_task1(WEIGHT_PATH, CLASS_NAMES)
    client4.run_task1(WEIGHT_PATH, CLASS_NAMES)

