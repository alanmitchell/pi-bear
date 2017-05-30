#!/usr/bin/python

import time
from datetime import datetime
import os
import shutil
import picamera
import RPi.GPIO as GPIO

class Camera:

    def __init__(self, file_dir):
        self.file_dir = file_dir
        self.tmp_img_file = os.path.join(os.path.dirname(__file__), 'tmp.h264')
        self.is_on = False

    def camera_start(self):
        # need to store in a temporary image file because file is constantly
        # changing while recording is occurring, and don't want to have a
        # partial file in the final media directory.
        self.camera = picamera.PiCamera()
        self.camera.start_recording(self.tmp_img_file)
        self.is_on = True
        print 'Camera On'

    def camera_stop(self):
        self.camera.stop_recording()
        self.close()
        self.is_on = False
        print 'Camera Off'
        fname = os.path.join(self.file_dir,
                             datetime.now().strftime('%Y-%m-%d-%H%M%S') + '.h264')
        shutil.copy(self.tmp_img_file, fname)

    def close(self):
        self.camera.close()


class MotionSensor:

    def __init__(self, pins):

        # list of pins that have motion sensors on them
        self.pins = pins

        # Last motion state
        self.state = False

        # timestamp of when last motion occurred
        self.last_motion_ts = 0.0

        # Set up GPIO module and motion sensor input pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in pins:
            GPIO.setup(pin, GPIO.IN)

    def read(self):

        # count the number of sensors with motion
        moving_sensors = sum([GPIO.input(p) for p in self.pins])
        
        if moving_sensors:
            self.last_motion_ts = time.time()
            self.state = True
        else:
            self.state = False

    def time_since_last_motion(self):
        return time.time() - self.last_motion_ts


if __name__=='__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Bear Camera')
    parser.add_argument('media_dir', help='directory where video/image files will be stored')
    parser.add_argument('-w', '--wait',
                        help='wait in seconds before turning camera off after motion',
                        type=float,
                        default=0.5)

    args = parser.parse_args()

    try:

        cam = Camera(args.media_dir)
        motion = MotionSensor([22, 23])

        while True:
            motion.read()
            if cam.is_on:
                if motion.time_since_last_motion() > args.wait:
                    cam.camera_stop()

            else:
                if motion.state:
                    cam.camera_start()
        
            time.sleep(0.2)

    finally:
        cam.close()
