from mobilenettest import MobileNetTest
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from settings import *
from clientinstance import ClientInstance


class Server:
    def __init__(self, host, port): # open socket
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((host, port))
        self.mobile_net_test = MobileNetTest(CLASS_NAMES, WEIGHT_PATH, INPUT_SHAPE)
        self.ci_list = []

    def run_task(self): # connect client
        self.socket.listen(1)
        print('Ready to accept client')

        thread_list = []
        for _ in range(NUMBER_OF_SEND_VIDEO):
            conn, addr = self.socket.accept()
            print('successfully connected', addr[0], ':', addr[1])
            ci = ClientInstance(self.mobile_net_test, conn)
            self.ci_list.append(ci)
            conn_thread = Thread(target=ci.main_task)
            conn_thread.start()
            thread_list.append(conn_thread)

        for conn_thread in thread_list:
            conn_thread.join()


if __name__ == '__main__':
    server = Server(SERVER_HOST, SERVER_PORT)
    server.run_task()
