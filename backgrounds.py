# fakevid2.py
#
# Zoom-alike VideoConference Background Replacer 
# 
# Copyright (c) 2020, Mauro A. Meloni <maumeloni@gmail.com>
# Licence: GPL
#

from os.path import exists

import cv2
import numpy as np


class GenericBackground:

    def __init__(self, filepath, framedata):
        if not exists(filepath):
            raise FileNotFoundError(filepath)
        self._filepath = filepath
        self._webcam_res = framedata.size
        self._webcam_fps = framedata.fps
        self._blur_level = 0

    def get_blur_level(self):
        return self._blur_level

    def set_blur_level(self, value):
        self._blur_level = value

    def _apply_blur(self):
        if self._blur_level:
            dims = (self._blur_level, self._blur_level)
            self._frame = cv2.blur(self._image.astype(float), dims)
        else:
            self._frame = self._image

    def get_frame(self):
        return NotImplementedError()


class StaticBackground(GenericBackground):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        image = cv2.imread(self._filepath)
        self._image = cv2.resize(image, self._webcam_res)
        self._frame = self._image

    def set_blur_level(self, value):
        super().set_blur_level(value)
        self._apply_blur()   # apply blur once

    def get_frame(self):
        return self._frame.copy()


class AnimatedBackground(GenericBackground):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._video = cv2.VideoCapture(self._filepath)
        self._properties = (
            self._video.get(cv2.CAP_PROP_FRAME_WIDTH),
            self._video.get(cv2.CAP_PROP_FRAME_HEIGHT),
            self._video.get(cv2.CAP_PROP_FPS),
        )
        self._need_resize = False
        if tuple(self._properties[0:1]) != self._webcam_res:
            self._need_resize = True
            print('Video resolution != Webcam resolution - Performance will be degraded')
        if self._properties[2] < self._webcam_fps:
            print('Video FPS < Webcam FPS - Background video will play faster than webcam video')
        elif self._properties[2] > self._webcam_fps:
            print('Video FPS > Webcam FPS - Background video will play slower than webcam video')
        self._frame = None
        self._framenum = 0
        self._framemax = 0

    def __del__(self):
        if self._video is not None:
            self._video.release()

    def get_frame(self):
        ret, frame = self._video.read()
        if ret:
            self._frame = frame
            self._framenum += 1
        else:
            # got to end, rewind
            self._framemax = self._framenum - 1
            self._video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._video.read()
            self._framenum = 1
            self._frame = frame
        if self._need_resize:
            self._frame = cv2.resize(self._frame, self._webcam_res)
        self._image = self._frame
        self._apply_blur()
        return self._frame

    def seek(self, seconds):
        self._framenum = self._video.get(cv2.CAP_PROP_POS_FRAMES)
        self._framenum += self._properties[2] * seconds
        self._video.set(cv2.CAP_PROP_POS_FRAMES, self._framenum)

