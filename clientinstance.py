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
        self.communication_delay_list = []
        self.computation_start_time = 0
        self.computation_end_time = 0
        self.main_fps_start_time = 0
        self.fps_end_time = 0
        self.client_id = ' '

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
            data = self.conn.recv(16384)

            # When connection is closed or any problem, run close code
            if not data:
                # Zero is finish flag for MobileNetTest
                self.frame_queue.put((0, 0, 0, 0))
                return
            buffer += data

            while (b'Start_Symbol' in buffer) and (b'End_Symbol' in buffer):
                start_idx = buffer.find(b'Start_Symbol')
                id_idx = buffer.find(b'Id_Symbol')
                size_idx = buffer.find(b'Size_Symbol')
                frame_idx = buffer.find(b'Frame_Num')
                send_time_idx = buffer.find(b'Send_Time')
                end_idx = buffer.find(b'End_Symbol')

                self.client_id = buffer[start_idx+12: id_idx].decode(errors="ignore")
                body_size = buffer[id_idx+9:size_idx].decode(errors="ignore")
                frame_num = int(buffer[size_idx+11:frame_idx].decode(errors="ignore"))
                send_time = float(buffer[frame_idx+9:send_time_idx].decode(errors="ignore"))
                msg_body = buffer[send_time_idx+9:end_idx]

                if body_size.isdigit():
                    body_size = int(body_size)

                if len(msg_body) == body_size:
                    self._put_frame(body_size, frame_num, send_time, msg_body)
                    buffer = buffer[end_idx+10:]

    def _put_frame(self, body_size, frame_num, send_time, msg_body):
        self.put_count = self.put_count+1
        if body_size and len(msg_body) == body_size:
            image = numpy.load(BytesIO(msg_body))['frame']
            if self.frame_queue.qsize() < SERVER_QUEUE_SIZE:
                # measure communication delay
                self.communication_end_time = time.time()
                self.communication_delay_list.append(self.communication_end_time - send_time)
                self.frame_queue.put((image, send_time, self.client_id, frame_num))
            else:
                self.frame_drop_count += 1

    def run_test(self):
        while self.frame_queue.empty():
            continue

        self.computation_start_time = self.main_fps_start_time = time.time()
        while True:
            frame, send_time, client_id, frame_num = self.frame_queue.get()
            if frame is 0:
                self.fps_end_time = self.computation_end_time = time.time()
                self.return_procedure()
                return

            self.run_count = self.run_count + 1
            self.MBNet.run(frame, frame_num)

            print(client_id, "'s", frame_num,"frame processing complete")

    def return_procedure(self):
        avg_communication_delay = sum(self.communication_delay_list)/len(self.communication_delay_list)
        avg_computation_delay = (self.computation_end_time-self.computation_start_time)/NUMBER_OF_TOTAL_FRAME
        avg_main_fps = NUMBER_OF_TOTAL_FRAME/(self.fps_end_time - self.main_fps_start_time)
        avg_client_fps = avg_main_fps - avg_communication_delay * avg_main_fps

        print("\nResults of", self.client_id)
        print("Average communication delay : %.3f" % avg_communication_delay)
        print("Average computational delay : %.3f" % avg_computation_delay)
        print("Average Main(model) FPS : %.3f" % avg_main_fps)
        print("Average client FPS : %.3f" % avg_client_fps)
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
        print("Total runtime : %.3f" % (time.time() - start_time))