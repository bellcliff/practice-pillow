#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yangbo
# @Date:   2015-08-04 11:48:39
# @Last Modified by:   Yang Bo
# @Last Modified time: 2015-08-08 00:02:38

import os
import numpy
import time
from PIL import Image
from uiautomator import Device


DEVICE = Device('192.168.57.102:5555')
RECTS = {
    'back': (190, 700, 280, 720),
    'item': (295, 890, 425, 925),
    'continue': (125, 1125, 270, 1165),
    'start': (55, 1135, 150, 1175),
    #    'burn': (610, 675, 650, 695),
    'fight': (315, 1115, 400, 1155)
}
PATH_RES = 'resource'


class Crop:
    PATH_RES = 'resource'
    CACHE = dict()

    def __init__(self, name):
        self.name = name
        self. cropPath = '%s/%s_crop.png' % (Crop.PATH_RES, self.name)
        self.cropImg = Image.open(self.cropPath)
        self.box = RECTS[name]

    @property
    def rawPath(self):
        return '%s/%s.png' % (self.PATH_RES, self.name)

    @property
    def cropPath(self):
        return '%s/%s_crop.png' % (self.PATH_RES, self.name)

    def compare(self, img):
        a = img.crop(self.box)
        for x in range(0, a.size[0]):
            for y in range(0, a.size[1]):
                p = (x, y)
                pa = a.getpixel(p)
                pb = self.cropImg.getpixel(p)
                if pa != pb:
                    return False
        return True

    def click(self):
        x = int((self.box[0] + self.box[2])/2)
        y = int((self.box[1] + self.box[3])/2)
        DEVICE.click(x, y)

    @staticmethod
    def instance(name):
        if name not in Crop.CACHE:
            Crop.CACHE[name] = Crop(name)
        return Crop.CACHE[name]

    @staticmethod
    def act():
        img, path = screen()
        keepScreen = False
        for name in RECTS.keys():
            crop = Crop.instance(name)
            if crop.compare(img):
                crop.click()
                keepScreen = name in ['item']
                break
        if not keepScreen:
            os.remove(path)


def screen(screenName=None, path='imgs'):
    if screenName is None:
        screenName = time.strftime('%m_%d_%H_%M_%S.png', time.gmtime())
    screenPath = '%s/%s' % (path, screenName)
    DEVICE.screenshot(screenPath)
    return Image.open(screenPath), screenPath

if __name__ == '__main__':
    while True:
        Crop.act()
        time.sleep(1)
    # screen('continue.png', 'resource')
