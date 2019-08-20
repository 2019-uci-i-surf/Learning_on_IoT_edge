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
        self.conn_start_time = 0
        self.communication_delay = 0
        self.computational_delay_list = []

    def recv_data(self):
        if not self.conn:
            raise Exception("Connection is not established")
        self.conn.sendall(b'ready')
        self.conn_start_time = float(str(self.conn.recv(1024), 'utf-8'))
        body_size = None
        buffer = b''
        while True:
            data = self.conn.recv(16392)  # 1024 byte 로 frame cut
            # When connection is closed or any problem, run close code
            if not data:
                # Zero is finish flag for MobileNetTest
                self.frame_queue.put(0)
                return
            buffer += data
            while b'???' in buffer:
                header_idx = buffer.find(b'???')
                if header_idx != 0:
                    msg_body = buffer[:header_idx]
                    self._put_frame(body_size, msg_body)
                    buffer = buffer[header_idx:]
                    header_idx = 0
                if b':::' not in buffer:
                    buffer = b''
                    body_size = None
                    break
                size_idx = buffer.find(b':::')
                body_size = buffer[header_idx+3:size_idx].decode(errors="ignore")
                if body_size.isdigit():
                    body_size = int(body_size)
                else:
                    buffer = b''
                    body_size = None
                    break
                buffer = buffer[size_idx+3:]

    def _put_frame(self, body_size, msg_body):
        # check msg_body is whole
        if body_size and len(msg_body) == body_size:
            image = numpy.load(BytesIO(msg_body))['frame']

            # measure communication delay
            if not self.communication_delay:
                self.communication_delay = time.time() - self.conn_start_time

            if self.frame_queue.qsize() <= TCP_QUEUE_SIZE:
                self.frame_queue.put(image)

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
