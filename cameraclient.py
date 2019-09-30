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
                success, image = vidcap.read()
                if not success:
                    print('video is not opened!')
                    break
                count += 1
                bytes_io = BytesIO()
                numpy.savez_compressed(bytes_io, frame=image)
                bytes_io.seek(0)
                bytes_image = bytes_io.read() # byte per 1frame

                #
                msg = ('???' + str(len(bytes_image)) + ':::').encode() + bytes_image
                self.socket.sendall(msg)
                print("Now frame num : ", count, "frame size", str(len(bytes_image))) # print now frame number

            print("{} frames are sent.".format(count)) # print total frames

    @staticmethod
    def mp_routine(host, port):
        cc = CameraClient()
        cc.connect_to_server(host=host, port=port)
        cc.transmission(video_path=VIDEO_PATH)