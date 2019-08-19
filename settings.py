SERVER_HOST = '10.8.38.127'
#SERVER_PORT = 9999

WEIGHT_PATH = 'mobilenetssd300.hdf5'
CLASS_NAMES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
               "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
               "tvmonitor"]
DETECTION_LIST = ['person', 'chair', 'boat']

# This image queue size. Queue was gotten from the model
TCP_QUEUE_SIZE = 10