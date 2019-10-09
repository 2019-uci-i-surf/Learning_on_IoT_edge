import time
import numpy
from socket import socket, AF_INET, SOCK_STREAM
from io import BytesIO
from settings import *
import cv2
import time

VIDEO_PATH = r'Pexels Videos 1466210.mp4'

class CameraClient:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.time_list=[]
        self.frame_rate=[]

    def connect_to_server(self, host, port):
        print('try to connect to server..')
        self.socket.connect((host, port))
        print('successfully connected')

    def transmission(self, video_path):
        vidcap = cv2.VideoCapture(video_path)
        count = 0
        msg = str(self.socket.recv(1024), 'utf-8') # receive data(broadcast or ready) from server
        if msg == 'ready':
            self.socket.sendall(bytes(str(time.time()), encoding='utf-8'))
            while True:
                frame_start = time.time()
                success, image = vidcap.read()
                if not success:
                    print('video is not opened!')
                    break
                count += 1
                bytes_io = BytesIO()
                numpy.savez_compressed(bytes_io, frame=image)
                bytes_io.seek(0)
                bytes_image = bytes_io.read() # byte per 1frame

                msg = ('Start_Symbol' + CLIENT_ID + 'Id_Symbol' + str(len(bytes_image)) + 'Size_Symbol').encode() + bytes_image + ('End_Symbol').encode()
                self.socket.sendall(msg)
                print("Now frame num : ", count, "frame size", str(len(bytes_image))) # print now frame number

                sending_time = time.time() - frame_start
                self.time_list.append(sending_time)
                time_lists = self.time_list[-20:]
                self.frame_rate.append(len(time_lists) / sum(time_lists))

            print("{} frames are sent.".format(count)) # print total
            print("Avg Frame rate of sending:", sum(self.frame_rate) / len(self.frame_rate))

    @staticmethod
    def mp_routine(host, port):
        cc = CameraClient()
        cc.connect_to_server(host=host, port=port)
        cc.transmission(video_path=VIDEO_PATH)