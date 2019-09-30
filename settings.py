SERVER_HOST = '169.234.59.248'
SERVER_PORT = 10001

INPUT_SHAPE = (300, 300, 3)
WEIGHT_PATH = r'model/mobilenetssd300.hdf5'
CLASS_NAMES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
               "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
               "tvmonitor"]
DETECTION_LIST = ['person', 'chair', 'boat']
NUMBER_OF_SEND_VIDEO = 1

# This image queue size. Queue was gotten from the model
TCP_QUEUE_SIZE =20
