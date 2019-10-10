# Need to change on Both part
SERVER_HOST = '192.168.1.6'
SERVER_PORT = 10001

# Need to change on Client part
CLIENT_ID = "Laptop"
NUMBER_OF_SEND_VIDEO = 1
RATE_OF_SENDING_PART = 6

# Need to change on Server part
SERVER_QUEUE_SIZE = 40
NUMBER_OF_RECEIVE_CLIENT = 1

NUMBER_OF_TOTAL_FRAME = 461
VIDEO_PATH = r'Pexels Videos 1466210.mp4'
INPUT_SHAPE = (300, 300, 3)
WEIGHT_PATH = r'model/mobilenetssd300.hdf5'
CLASS_NAMES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
               "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
               "tvmonitor"]
DETECTION_LIST = ['person', 'chair', 'boat']


