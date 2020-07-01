import os
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import tensorflow as tf
import argparse
import sys
import RPi.GPIO as GPIO
import time

# Set up Servo Motor
servoPINmetal = 7
servoPINplastic = 11
servoPINpaper = 13
servoPINplatform1 = 15
servoPINplatform2 = 29

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPINmetal, GPIO.OUT)
GPIO.setup(servoPINplastic, GPIO.OUT)
GPIO.setup(servoPINpaper, GPIO.OUT)
GPIO.setup(servoPINplatform1, GPIO.OUT)
GPIO.setup(servoPINplatform2, GPIO.OUT)

sMetal = GPIO.PWM(servoPINmetal, 50)
sPlastic = GPIO.PWM(servoPINplastic, 50)
sPaper = GPIO.PWM(servoPINpaper, 50)
sPlatform1 = GPIO.PWM(servoPINplatform1, 50)
sPlatform2 = GPIO.PWM(servoPINplatform2, 50)

sMetal.start(7.5)
sPlastic.start(7.5)
sPaper.start(7.5)
sPlatform1.start(7.5)
sPlatform2.start(7.5)

sMetal.ChangeDutyCycle(0)
sPlastic.ChangeDutyCycle(0)
sPaper.ChangeDutyCycle(0)
sPlatform1.ChangeDutyCycle(0)
sPlatform2.ChangeDutyCycle(0)

# Set up camera constants
IM_WIDTH = 640
IM_HEIGHT = 480   

# The working directory is the object_detection folder.
sys.path.append('..')

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Directory containing the object detection module
MODEL_NAME = 'item_model'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'data','item_labelmap.pbtxt')

# Number of classes the object detector can identify
NUM_CLASSES = 3

# Load the label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)


# Define input and output tensors (i.e. data) for the object detection classifier
# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects together with class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize camera
camera = PiCamera()
camera.resolution = (IM_WIDTH,IM_HEIGHT)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(IM_WIDTH,IM_HEIGHT))
rawCapture.truncate(0)        

for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    t1 = cv2.getTickCount()
    # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value
    frame = np.copy(frame1.array)
    frame.setflags(write=1)
    frame_expanded = np.expand_dims(frame, axis=0)

    # Perform detection
    start_time = time.time()
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})
    end_time = time.time()
    print("Inference time = " + str(start_time-end_time))
    
    # Display result of detection in frame
    vis_util.visualize_boxes_and_labels_on_image_array(
        frame,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.40)

    cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),font,1,(255,255,0),2,cv2.LINE_AA)

    cv2.imshow('Object detector', frame)

    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc = 1/time1
        
    className = ([(category_index.get(value)).get('name') for index,value in enumerate(classes[0]) if scores[0,index] > 0.5])
    x = ''.join(className)
    print(x)
    
    # If metal is detected
    if x == "metal":
        sMetal.ChangeDutyCycle(7.5)
        time.sleep(1)
        sPlatform2.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPlatform1.ChangeDutyCycle(5)
        time.sleep(0.2)
        sPlatform1.ChangeDutyCycle(0)
        time.sleep(2)
        sPlatform1.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPlatform2.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        sMetal.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sMetal.ChangeDutyCycle(0)
        sPlatform1.ChangeDutyCycle(0)
        sPlatform2.ChangeDutyCycle(0)
            
    # If plastic is detected
    elif x == "plastic":
        sPlastic.ChangeDutyCycle(6.5)
        time.sleep(1)
        sPlatform2.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPlatform.ChangeDutyCycle(7)
        time.sleep(0.3)
        sPlatform.ChangeDutyCycle(0)
        time.sleep(2)
        sPlatform.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPlatform2.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        sPlastic.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPlastic.ChangeDutyCycle(0)
        sPlatform.ChangeDutyCycle(0)
        sPlatform2.ChangeDutyCycle(0)
            
    # If paper is detected
    elif x == "paper":
        sPaper.ChangeDutyCycle(6.5)
        time.sleep(1)
        sPlatform2.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPlatform.ChangeDutyCycle(7.5)
        time.sleep(0.2)
        sPlatform.ChangeDutyCycle(0)
        time.sleep(2)
        sPlatform.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPlatform2.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        sPaper.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        sPaper.ChangeDutyCycle(0)
        sPlatform.ChangeDutyCycle(0)
        sPlatform2.ChangeDutyCycle(0)
        
    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

    rawCapture.truncate(0)

camera.close()

cv2.destroyAllWindows()

