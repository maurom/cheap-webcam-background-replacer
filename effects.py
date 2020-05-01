# fakevid2.py
#
# Zoom-alike VideoConference Background Replacer 
# 
# Copyright (c) 2020, Mauro A. Meloni <maumeloni@gmail.com>
# Licence: GPL
#

import cv2
import numpy as np

from main import DEBUG


class AddTextEffect:

    def __init__(self, text, position=(0, 0), color=(255, 255, 255)):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.text = text
        self.color = color

    def apply(self, framedata):
        cv2.putText(framedata.background, self.text, self.position, self.font, 1, self.color, 2, cv2.LINE_AA)


class ShadowEffect:

    def __init__(self, opacity=0.7, blur=100):
        self.opacity = opacity
        self.blur = blur
        self._displacement = None
        self._translation_matrix = None
        self.set_displacement(30, 10)

    def set_displacement(self, x, y):
        self._displacement = (x, y)
        self._translation_matrix = np.float32(([1, 0, x], [0, 1, y]))   # shadow displacement

    def get_displacement(self):
        return self._displacement

    def apply(self, framedata):
        if not self.opacity:
            return
        dims = (self.blur, self.blur)
        shadow = cv2.dilate(framedata.mask, np.ones((20, 20), np.uint8), iterations=1)
        shadow = cv2.blur(1 - shadow * self.opacity, dims)    # shadow definition
        shadow = cv2.warpAffine(shadow, self._translation_matrix, framedata.size, borderValue=1.0)
        # shadow = np.repeat(shadow[:, :, np.newaxis], 3, axis=2)
        for c in range(framedata.background.shape[2]):
            framedata.background[:,:,c] = framedata.background[:,:,c] * shadow
        if DEBUG:
            cv2.imshow('shadow', shadow)


class HologramEffect:

    def __init__(self):
        pass

    def apply(self, framedata):
        # add a blue tint
        holo = cv2.applyColorMap(framedata.output, cv2.COLORMAP_WINTER)
        # add a halftone effect
        bandLength, bandGap = 2, 3
        for y in range(holo.shape[0]):
            if y % (bandLength+bandGap) < bandLength:
                holo[y,:,:] = holo[y,:,:] * np.random.uniform(0.1, 0.3)
        # add some ghosting
        holo_blur = cv2.addWeighted(holo, 0.2, self._shift_image(holo.copy(), 5, 5), 0.8, 0)
        holo_blur = cv2.addWeighted(holo_blur, 0.4, self._shift_image(holo.copy(), -5, -5), 0.6, 0)
        # combine with the original color, oversaturated
        framedata.output = cv2.addWeighted(framedata.output, 0.5, holo_blur, 0.6, 0)

    def _shift_image(self, img, dx, dy):
        img = np.roll(img, dy, axis=0)
        img = np.roll(img, dx, axis=1)
        if dy>0:
            img[:dy, :] = 0
        elif dy<0:
            img[dy:, :] = 0
        if dx>0:
            img[:, :dx] = 0
        elif dx<0:
            img[:, dx:] = 0
        return img

