import numpy
import time
from io import BytesIO
from settings import *
from threading import Thread

class ClientInstance:
    def __init__(self, MBNet, conn, addr, queue):
        self.MBNet = MBNet
        self.conn = conn
        self.addr = addr
        self.conn_start_time = 0
        self.computation_start_time = 0
        self.computation_end_time = 0
        self.main_fps_start_time = 0
        self.fps_end_time = 0
        self.client_id = ' '
        self.communication_delay = 0.0

        self.receive_count = 0
        self.put_count = 0
        self.run_count = 0
        self.frame_drop_count = 0

        self.frame_queue = queue

    def recv_data(self):
        if not self.conn:
            raise Exception("Connection is not established")
        self.conn.sendall(b'broadcast_start')
        print("Broadcast to Device")
        body_size = None
        buffer = b''

        while True:
            self.receive_count=self.receive_count+1
            data = self.conn.recv(32768)
            buffer += data

            while (b'Start_Symbol' in buffer) and (b'End_Symbol' in buffer):
                start_idx = buffer.find(b'Start_Symbol')
                id_idx = buffer.find(b'Id_Symbol')
                size_idx = buffer.find(b'Size_Symbol')
                frame_idx = buffer.find(b'Frame_Num')
                end_idx = buffer.find(b'End_Symbol')

                self.client_id = buffer[start_idx+12: id_idx].decode(errors="ignore")
                body_size = buffer[id_idx+9:size_idx].decode(errors="ignore")
                frame_num = int(buffer[size_idx+11:frame_idx].decode(errors="ignore"))
                msg_body = buffer[frame_idx+9:end_idx]

                if body_size.isdigit():
                    body_size = int(body_size)

                if len(msg_body) == body_size:
                    self.conn.sendall(str(frame_num).encode())
                    self._put_frame(body_size, frame_num, msg_body)
                    buffer = buffer[end_idx+10:]

                if frame_num == NUMBER_OF_TOTAL_FRAME:
                    data = self.conn.recv(1024)
                    self.communication_delay = data.decode(errors="ignore")
                    return

    def _put_frame(self, body_size, frame_num, msg_body):
        self.put_count = self.put_count+1
        if body_size and len(msg_body) == body_size:
            image = numpy.load(BytesIO(msg_body))['frame']
            if self.frame_queue.qsize() < SERVER_QUEUE_SIZE:
                self.frame_queue.put((image, self.client_id, frame_num))
            else:
                self.frame_drop_count += 1

    def run_test(self):
        while self.frame_queue.empty():
            continue
        self.computation_start_time = self.main_fps_start_time = time.time()
        while True:
            frame, client_id, frame_num = self.frame_queue.get()
            self.run_count = self.run_count + 1
            self.MBNet.run(frame, frame_num)

            print(client_id, "'s", frame_num, "frame processing complete")

            if frame_num == NUMBER_OF_TOTAL_FRAME:
                self.fps_end_time = self.computation_end_time = time.time()
                self.return_procedure()
                return

    def return_procedure(self):
        avg_communication_delay = float(self.communication_delay)
        avg_computation_delay = (self.computation_end_time-self.computation_start_time)/NUMBER_OF_TOTAL_FRAME
        avg_main_fps = NUMBER_OF_TOTAL_FRAME/(self.fps_end_time - self.main_fps_start_time)
        avg_client_fps = avg_main_fps - avg_communication_delay * avg_main_fps

        print("\nResults of", self.client_id)
        print("Average communication delay :", avg_communication_delay)
        print("Average computational delay :", avg_computation_delay)
        print("Average Main(model) FPS :", avg_main_fps)
        print("Average client FPS :", avg_client_fps)
        print("Put_into_frame_count :", self.put_count)
        print("Run_count :", self.run_count)
        print("Frame_drop :", self.frame_drop_count)

    def main_task(self):
        start_time = time.time()
        recv_thread = Thread(target=self.recv_data)
        run_thread = Thread(target=self.run_test)
        recv_thread.start()
        run_thread.start()
        recv_thread.join()
        run_thread.join()
        print("Total runtime :", (time.time() - start_time), "sec")