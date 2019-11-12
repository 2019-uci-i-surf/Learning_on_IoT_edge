from mobilenettest import MobileNetTest
from socket import socket, AF_INET, SOCK_STREAM
from multiprocessing import Process
from settings import *
from clientinstance import ClientInstance
from queue import Queue

class Server:
    def __init__(self, host, port): # open socket
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((host, port))
        self.mobile_net_test = MobileNetTest(CLASS_NAMES, WEIGHT_PATH, INPUT_SHAPE)
        self.ci_list = []
        self.frame_queue = Queue()

    def run_task(self): # connect client
        self.socket.listen(1)
        print('Ready to accept client')

        process_list = []
        for _ in range(NUMBER_OF_RECEIVE_VIDEOS):
            conn, addr = self.socket.accept()
            print('successfully connected', addr[0], ':', addr[1])
            ci = ClientInstance(self.mobile_net_test, conn, addr, self.frame_queue)
            self.ci_list.append(ci)

        for ci in self.ci_list:
            conn_process = Process(target=ci.main_task)
            conn_process.start()
            process_list.append(conn_process)

        for conn_process in process_list:
            conn_process.join()

if __name__ == '__main__':
    server = Server(SERVER_HOST, SERVER_PORT)
    server.run_task()
