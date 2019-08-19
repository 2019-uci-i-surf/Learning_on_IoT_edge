from mobilenettest import MobileNetTest
from socket import socket, AF_INET, SOCK_STREAM
import numpy
from io import BytesIO
from queue import Queue
from threading import Thread
from settings import *
import time

class ProcessingServer:
    def __init__(self, host, port): # open socket
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((host, port))
        self.mobile_net_test = None
        self.image_queue = Queue()

    def listen_client(self): # connect client
        self.socket.listen(1)
        print('Ready to accept client')

        self.conn_list = []
        for _ in range(2):
            conn, addr = self.socket.accept()
            print('successfully connected', addr[0], ':', addr[1])
            conn_thread = Thread(target=self.recv_data, args=(conn,))
            conn_thread.start()
            self.conn_list.append(conn_thread)

        for conn_thread in self.conn_list:
            conn_thread.join()
            print('\nData Transmission End Time :', time.strftime('%Y-%m-%d-%X', time.localtime(time.time())))

    def recv_data(self, conn):
        if not conn:
            raise Exception("Connection is not established")
        msg_body = None
        body_size = None
        while True:
            data = conn.recv(1024) # 1024 byte 로 frame cut
            # When connection is closed or any problem, run close code
            if not data:
                #Zero is finish flag for MobileNetTest
                self.image_queue.put(0)
                return
            # check header
            if b'SIZE1' in data: # 새로운 frame이 들어왔을 때
                header_idx = data.find(b'SIZE') # start symbol
                if msg_body:
                    msg_body += data[:header_idx]
                    self.put_recv_data(msg_body, body_size)
                split_msg = data[header_idx:].split(b':')
                if len(split_msg) < 3: # 잘 못된 데이터가 들어왔을 때
                    continue
                body_size = int(split_msg[1].decode())
                msg_body = split_msg[2]
            else:
                msg_body += data


    def put_recv_data(self, msg_body, body_size):
        if len(msg_body) != body_size:
            return
        image = numpy.load(BytesIO(msg_body))['frame']
        if self.image_queue.qsize() <= TCP_QUEUE_SIZE:
            self.image_queue.put(image)

    def communication_task(self):
        self.listen_client()

    def model_test_task(self, weight_path, class_names):
        input_shape = (640, 360, 3)
        self.mobile_net_test = MobileNetTest(class_names, weight_path, input_shape)
        self.mobile_net_test.run(self.image_queue)
        return

    def run_task1(self, weight_path, class_names):
        # communication thread section
        communication_thread = Thread(target=self.communication_task)
        communication_thread.start()
        # running model section
        model_test_thread = Thread(target=self.model_test_task, args=(weight_path, class_names))
        model_test_thread.start()
        communication_thread.join()
        model_test_thread.join()


if __name__ == '__main__':
    client = ProcessingServer(SERVER_HOST, 10001)
    client.run_task1(WEIGHT_PATH, CLASS_NAMES)
