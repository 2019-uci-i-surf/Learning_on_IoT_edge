import numpy
import time
from io import BytesIO
from queue import Queue
from settings import TCP_QUEUE_SIZE
from threading import Thread


class ClientInstance:

    def __init__(self, MBNet, conn, addr):
        self.MBNet = MBNet
        self.frame_queue = Queue()
        self.conn = conn
        self.addr = addr
        self.communication_delay = 0
        self.computational_delay_list = []

    def recv_data(self):
        if not self.conn:
            raise Exception("Connection is not established")
        self.conn.sendall(b'ready')
        start_time = float(str(self.conn.recv(1024), 'utf-8'))
        msg_body = None
        body_size = None
        while True:
            data = self.conn.recv(8192)  # 1024 byte 로 frame cut
            # When connection is closed or any problem, run close code
            if not data:
                # Zero is finish flag for MobileNetTest
                self.frame_queue.put(0)
                return
            # check header
            if b'SIZE' in data:  # 새로운 frame이 들어왔을 때
                header_idx = data.find(b'SIZE')  # start symbol
                if msg_body:
                    msg_body += data[:header_idx]

                    if len(msg_body) != body_size:
                        return
                    image = numpy.load(BytesIO(msg_body))['frame']

                    # measure communication delay
                    if not self.communication_delay:
                        self.communication_delay = time.time() - start_time

                    if self.frame_queue.qsize() <= TCP_QUEUE_SIZE:
                        self.frame_queue.put(image)

                split_msg = data[header_idx:].split(b'???')
                if len(split_msg) < 3:  # 잘못된 데이터가 들어왔을 때
                    print(split_msg)
                    continue
                body_size = int(split_msg[1].decode())
                msg_body = split_msg[2]
            else:
                msg_body += data

    def calc_fps(self):
        pass

    def run_test(self):
        while self.frame_queue.empty():
            continue

        while True:
            start_time = time.time()
            frame = self.frame_queue.get()

            if frame is 0:
                self.return_procedure()
                return
            self.MBNet.run(frame)

            # measure computation delay
            self.computational_delay_list.append(time.time() - start_time)

    def return_procedure(self):
        print("result of {}:{}".format(self.addr[0], self.addr[1]))
        print("communication delay: %.4f" % (self.communication_delay))
        print("computational delay: %.4f" % (sum(self.computational_delay_list)/len(self.computational_delay_list)))

    def main_task(self):
        recv_thread = Thread(target=self.recv_data)
        recv_thread.start()
        test_thread = Thread(target=self.run_test)
        test_thread.start()
        recv_thread.join()
        test_thread.join()
