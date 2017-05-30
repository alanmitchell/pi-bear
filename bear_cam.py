#!/usr/bin/python

import time
from datetime import datetime
import os
import picamera
import RPi.GPIO as GPIO

class Camera:

    def __init__(self, file_dir):
        self.file_dir = file_dir
        self.camera = picamera.PiCamera()
        self.is_on = False

    def camera_start(self):
        fname = os.path.join(self.file_dir,
            datetime.now().strftime('%Y-%m-%d-%H%M%S') + '.h264')
        self.camera.start_recording(fname)
        self.is_on = True
        print 'Camera On'

    def camera_stop(self):
        self.camera.stop_recording()
        self.is_on = False
        print 'Camera Off'


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

    # Amount of time to wait after last motion detection
    # before shutting off camera.
    WAIT_FOR_OFF = 4  # seconds

    try:

        cam = Camera('~/media')
        motion = MotionSensor([22, 23])

        while True:
            motion.read()
            if cam.is_on:
                if motion.time_since_last_motion() > WAIT_FOR_OFF:
                    cam.camera_stop()

            else:
                if motion.state:
                    cam.camera_start()
        
            time.sleep(0.2)

    finally:
        cam.close()