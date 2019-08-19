import numpy
from io import BytesIO
from queue import Queue
from settings import TCP_QUEUE_SIZE
from threading import Thread


class ClientInstance:

    def __init__(self, MBNet, conn):
        self.frame_queue = Queue()
        self.conn = conn
        self.MBNet = MBNet
        self.server_flag = False

    def recv_data(self):
        if not self.conn:
            raise Exception("Connection is not established")
        msg_body = None
        body_size = None
        while True:
            data = self.conn.recv(1024)  # 1024 byte 로 frame cut
            # When connection is closed or any problem, run close code
            if not data:
                # Zero is finish flag for MobileNetTest
                self.frame_queue.put(0)
                return
            # check header
            if b'SIZE1' in data:  # 새로운 frame이 들어왔을 때
                header_idx = data.find(b'SIZE')  # start symbol
                if msg_body:
                    msg_body += data[:header_idx]
                    self._put_frame(msg_body, body_size)
                split_msg = data[header_idx:].split(b':')
                if len(split_msg) < 3:  # 잘 못된 데이터가 들어왔을 때
                    continue
                body_size = int(split_msg[1].decode())
                msg_body = split_msg[2]
            else:
                msg_body += data

    def _put_frame(self, msg_body, body_size):
        if len(msg_body) != body_size:
            return
        image = numpy.load(BytesIO(msg_body))['frame']
        if self.frame_queue.qsize() <= TCP_QUEUE_SIZE:
            self.frame_queue.put(image)

    def calc_fps(self):
        pass

    def calc_communication_delay(self):
        pass

    def calc_computation_delay(self):
        pass

    def ready_callback(self):
        self.server_flag = True

    def run_test(self):
        # while not self.server_flag:
        #     continue

        while True:
            frame = self.frame_queue.get()
            if frame is 0:
                return
            self.MBNet.run(frame)

    def main_task(self):
        recv_thread = Thread(target=self.recv_data)
        recv_thread.start()
        test_thread = Thread(target=self.run_test)
        test_thread.start()
        recv_thread.join()
        test_thread.join()
