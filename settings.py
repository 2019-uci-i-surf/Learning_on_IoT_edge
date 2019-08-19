SERVER_HOST = 'localhost'
SERVER_PORT = 10001

INPUT_SHAPE = (640, 360, 3)
WEIGHT_PATH = 'mobilenetssd300.hdf5'
CLASS_NAMES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
               "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
               "tvmonitor"]
DETECTION_LIST = ['person', 'chair', 'boat']
NUMBER_OF_SEND_VIDEO = 2

# This image queue size. Queue was gotten from the model
TCP_QUEUE_SIZE = 10