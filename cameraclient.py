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
        start = time.time()
        vidcap = cv2.VideoCapture(video_path)
        count = 0
        while True:
            if(time.strftime('%S', time.localtime(time.time())) == '00'):
                break
        print('\nData Transmission Start Time :', time.strftime('%Y-%m-%d-%X', time.localtime(time.time())))
        while True:
            success, image = vidcap.read()
            if not success:
                print('video is not opened!')
                break
            #print('Read a new frame: ', success)
            #image1 = image.resize(300, 300)
            #print('shape', type(image1))
            #print(type(image))
            count += 1
            bytes_io = BytesIO()
            numpy.savez_compressed(bytes_io, frame=image)
            bytes_io.seek(0)
            bytes_image = bytes_io.read() # byte per 1frame

            # This is protocol that was defined by me
            header = ( 'SIZE1:' +str(len(bytes_image)) + ':').encode()
            self.socket.send(header) # send to server 1frame

            # send all raw bytes image
            body = bytes_image
            self.socket.sendall(body)
            #print(header)
            #print(body)
            #print()print("time :", time.time() - start)
            print("Now frame num {}: ".format(count)) # print now frame number

        print("{} frames are sent.".format(count)) # print total frames

    @staticmethod
    def mp_routine(host, port):
        cc = CameraClient()
        cc.connect_to_server(host=host, port=port)
        cc.transmission(video_path=VIDEO_PATH)