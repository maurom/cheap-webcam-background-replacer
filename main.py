#!/usr/bin/env python3
#
# Zoom-alike VideoConference Background Replacer
#
# Copyright (c) 2020, Mauro A. Meloni <maumeloni@gmail.com>
# Licence: GPL
#

from argparse import ArgumentParser
from os import system
from os.path import splitext

import cv2
import numpy as np
import pyfakewebcam

from backgrounds import *
from effects import *

#
# modprobe v4l2loopback devices=1 video_nr=20 card_label="v4l2loopback" exclusive_caps=1
#
# mpv av://v4l2:/dev/video20
DEBUG = False
USE_V4L2LOOPBACK = True


class BackgroundReplacer:

    def __init__(self, in_dev_path='/dev/video0', out_dev_path='/dev/video20'):
        self._window_title = 'BackgroundReplacer'
        self._in_dev_path = in_dev_path
        self._input_dev = None
        self._background = None
        self._output_dev = None
        self._bgsub = BackgroundSustractor()
        self.frame = FrameData()
        self.effects = []
        self.init_capture_device()
        if USE_V4L2LOOPBACK:
            if out_dev_path:
                # setup the fake camera
                self._output_dev = pyfakewebcam.FakeWebcam(out_dev_path, self.frame.size[0], self.frame.size[1])
            else:
                print('No output device specified. Please specify --output /dev/videoNN')

    def __del__(self):
        # When everything done, release the capture
        if self._input_dev is not None:
            self._input_dev.release()
        # if self._output_dev is not None:
        #     self._output_dev.release()

    def query_capabilities(self):
        # http://trac.gateworks.com/wiki/linux/v4l2
        system('v4l2-ctl -d %s' % self.in_dev_path)
        system('v4l2-ctl -d %s --list-formats-ext' % self.in_dev_path)

    def init_capture_device(self):
        # setup access to the *real* webcam
        resolutions = (
             (640, 480, 30),   # preferred for 4:3 webcams
             (176, 144, 30),
             (352, 288, 30),
             (320, 240, 30),
             (640, 360, 30),   # preferred for wide webcams
            (1280, 720, 10),
        )
        selected_resolution = 4
        width, height, fps = resolutions[selected_resolution]
        self._input_dev = cv2.VideoCapture(self._in_dev_path)
        self._input_dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._input_dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._input_dev.set(cv2.CAP_PROP_FPS, fps)
        FrameData.size = (width, height)
        FrameData.fps = fps

    def set_background(self, filepath):
        _, ext = splitext(filepath)
        if ext in ['.jpg', '.png']:
            self._background = StaticBackground(filepath, self.frame)
        elif ext in ['.mp4']:
            self._background = AnimatedBackground(filepath, self.frame)
        else:
            raise RuntimeError('Invalid background format: %s. Valid extensions: jpg, png, mp4' % filepath)

    def add_effect(self, effect):
        if effect not in self.effects:
            self.effects.append(effect)

    def _apply_background(self):
        inv_mask = 1 - self.frame.mask
        frame = self.frame.output
        for c in range(frame.shape[2]):
            frame[:,:,c] = frame[:,:,c] * self.frame.mask + self.frame.background[:,:,c] * inv_mask
        self.frame.output = frame

    def show_help(self):
        print('(q)uit - (b)lur level - (f)orward bg video - (r)eset bg mask - (d)isable bg replace')

    def run(self):
        # run forever, or at least until 'q' is pressed
        self.show_help()
        if self._background is None:
            self.set_background('background-t1r.jpg')
        text1 = AddTextEffect('Recording background', (10, 10))
        text2 = AddTextEffect('Move away from the camera!', (10, 10))
        disabled = False
        while True:
            ret, frame = self._input_dev.read()
            if DEBUG:
                cv2.imshow('input_frame', frame)
            self.frame.webcam = frame
            self.frame.output = frame
            self.frame.background = self._background.get_frame()
            self.frame.mask = self._bgsub.get_mask(self.frame)
            if DEBUG:
                cv2.imshow('mask', self.frame.mask)
            if self._bgsub.is_learning():
                print('Learning ...', self._bgsub._framenum)
                if text1 in self.effects:
                    self.effects.append(text1)
                    self.effects.append(text2)
            elif text1 in self.effects:
                self.effects.remove(text1)
                self.effects.remove(text2)
                self.show_help()
            for effect in self.effects:
                effect.apply(self.frame)
            if not disabled:
                self._apply_background()
            cv2.imshow('Fake Webcam Output', self.frame.output)
            if self._output_dev is not None:
                # fake webcam expects RGB
                frame = cv2.cvtColor(self.frame.output, cv2.COLOR_BGR2RGB)
                self._output_dev.schedule_frame(frame)
            key = chr(cv2.waitKey(1) & 0xFF).lower()
            if key == 'b':
                blur_level = self._background.get_blur_level()
                if blur_level < 20:
                    blur_level += 3
                else:
                    blur_level = 0
                self._background.set_blur_level(blur_level)
                print('  blur level set to %s' % blur_level)
            elif key == 'd':
                disabled = not disabled
                if disabled:
                    print('  background replacement disabled')
                else:
                    print('  background replacement enabled')
            elif key == 'f':
                if isinstance(self._background, VideoBackground):
                    self._background.seek(5)
                    fn = self._background._framenum * self._background._properties[2]
                    print('  advanced background to %d:%d' % (fn // 60, fn % 60))
                else:
                    print('  cannot seek on a static image')
            elif key == 'q':
                break
            elif key == 'r':
                print('   mask cleared')
                self._bgsub.forget_mask()
        cv2.destroyAllWindows()


class FrameData:

    size = None
    fps = None
    number = 0

    def __init__(self):
        self.webcam = None
        self.background = None
        self.output = None


class BackgroundSustractor:

    def __init__(self):
        # https://docs.opencv.org/3.4/d7/d7b/classcv_1_1BackgroundSubtractorMOG2.html
        self._bgsub = cv2.createBackgroundSubtractorMOG2()
        # https://docs.opencv.org/3.4/db/d88/classcv_1_1BackgroundSubtractorKNN.html
        # self.bg_substractor = cv2.createBackgroundSubtractorKNN()
        # self.bg_substractor = cv2.createBackgroundSubtractorGMG()
        self.blur_mask = True
        self._learning_frames = 30
        self._framenum = 0

    def forget_mask(self):
        self._framenum = 0

    def is_learning(self):
        return self._framenum < self._learning_frames

    def postprocess_mask(self, mask):
        mask = cv2.medianBlur(mask, 3)
        # https://docs.opencv.org/master/d7/d4d/tutorial_py_thresholding.html
        # _, mask = cv2.threshold(mask, 120, 255, cv2.THRESH_TOZERO)
        _, mask = cv2.threshold(mask, 120, 255, cv2.THRESH_BINARY)
        mask = cv2.erode(mask, np.ones((6, 6), np.uint8), iterations=1)   # cut borders to remove halo
        mask = self.imfill(mask)
        #cv2.imshow('imfill', mask)
        #mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
        #mask = cv2.erode(mask, np.ones((4, 4), np.uint8), iterations=1)
        #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.blur(mask.astype(float), (7, 7))
        return mask

    def imfill(self, input):
        im_th = input
        im_floodfill = im_th.copy()
        h, w = im_th.shape[:2]
        # Floodfill from point (0, 0)
        # cv2.imshow('input', input)
        mask = np.zeros((h+2, w+2), np.uint8)
        cv2.floodFill(im_floodfill, mask, (0, 0), 255);
        input = input + (255 - im_floodfill)
        return input

    def imfill_alt(self, input):
        im_th = input
        im_floodfill = im_th.copy()
        h, w = im_th.shape[:2]
        # Floodfill from point (0, 0)
        cv2.imshow('input', input)
        mask = np.zeros((h+2, w+2), np.uint8)
        cv2.floodFill(im_floodfill, mask, (0, 0), 127);
        # cv2.imshow('imfill2', im_floodfill)
        mask = np.zeros((h+2, w+2), np.uint8)
        cv2.floodFill(im_floodfill, mask, (0, 0), 255);
        mask = mask[1:-1, 1:-1]
        cv2.imshow('imfill3', (1 - mask) * 255)
        im_out = input + (1 - mask) * input
        cv2.imshow('im_out', im_out)
        #th, im_th = cv2.threshold(im_floodfill, 220, 255, cv2.THRESH_BINARY_INV)
        #cv2.imshow('imfill2', im_th)
        # Invert floodfilled image
        #im_floodfill_inv = cv2.bitwise_not(im_floodfill)
        # Combine the two images to get the foreground.
        #im_out = im_th | im_floodfill_inv
        return im_out

    def get_mask(self, framedata):
        frame = framedata.webcam
        if self._framenum < self._learning_frames:
            self._framenum += 1
            learningRate = -1
        else:
            learningRate = 0
        if self.blur_mask:
            frame = cv2.blur(frame.astype(float), (5, 5))
        self.mask = self._bgsub.apply(frame, learningRate=learningRate)
        self.mask = self.postprocess_mask(self.mask)
        self.mask /= 255.0
        return self.mask



if __name__ == '__main__':
    parser = ArgumentParser(description='Replace webcam background with a static image or video.')
    parser.add_argument('--background', '--bg', type=str, default='backgrounds/tatooine.jpg',
                        help='image or video which will be used as background')
    parser.add_argument('--shadow', action='store_true', default=False, help='adds shadow effect')
    parser.add_argument('--hologram', action='store_true', default=False, help='adds hologram effect')
    parser.add_argument('--blur', type=int, default=0, help='background blur level')
    parser.add_argument('--input', type=str, default='/dev/video0', help='input video device (webcam)')
    parser.add_argument('--output', type=str, help='output video device (optional pyfake device)')
    parser.add_argument('--debug', action='store_true', default=False)

    args = parser.parse_args()
    backgrounds_directory = './backgrounds/'
    if args.debug:
        DEBUG = True
    app = BackgroundReplacer(args.input, args.output)
    app.set_background(args.background)
    if args.shadow:
        app.add_effect(ShadowEffect())
    if args.hologram:
        app.add_effect(HologramEffect())
    if args.blur:
        app._background.set_blur_level(args.blur)
    #app.set_background(backgrounds_directory + 'backvan.jpg')
    #app.set_background(backgrounds_directory + 'thisisfine.jpg')
    #app.set_background(backgrounds_directory + 'background-t1r.jpg')
    #app.set_background('zoom-backgrounds/star_wars_3.mp4')
    app.run()

