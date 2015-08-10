#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yangbo
# @Date:   2015-08-04 11:48:39
# @Last Modified by:   Yang Bo
# @Last Modified time: 2015-08-10 10:19:56

import os
import sys
import json
import time
import numpy
from PIL import Image
from uiautomator import Device


DEVICE = Device('192.168.57.102:5555')
ACT_MODE = os.environ.get('ACT_MODE', 'endless')
with open('act.json') as actFile:
    RECTS = json.loads(actFile.read())[ACT_MODE]


class Crop:
    PATH_RES = 'resource/'+ACT_MODE
    CACHE = dict()

    def __init__(self, name):
        self.name = name
        self.cropPath = '%s/%s_crop.png' % (Crop.PATH_RES, self.name)
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

    def beforeClick(self):
        pass

    def afterClick(self):
        pass

    def afterCompare(self):
        # remove img after compare
        pass

    def click(self):
        x = int((self.box[0] + self.box[2])/2)
        y = int((self.box[1] + self.box[3])/2)
        DEVICE.click(x, y)

    @staticmethod
    def instance(name, mode='stage'):
        if name not in Crop.CACHE:
            if mode == 'stage':
                crop = StageCrop(name)
            else:
                crop = Crop(name)
            Crop.CACHE[name] = crop
        return Crop.CACHE[name]

    @staticmethod
    def act():
        img, path = screen()
        keepScreen = False
        for name in RECTS.keys():
            crop = Crop.instance(name)
            if crop.compare(img):
                crop.beforeClick()
                crop.click()
                crop.afterClick()
                keepScreen = name in ['item', 'continue']
                break
        if not keepScreen:
            os.remove(path)


class StageCrop(Crop):

    def afterClick(self):
        if self.name == 'continue' and ACT_MODE == 'stage':
            time.sleep(10)
            DEVICE.swipe(50, 350, 50, 100, steps=10)


def screen(screenName=None, path='imgs'):
    if screenName is None:
        screenName = time.strftime('%m%d_%H%M%S.png', time.gmtime())
    screenPath = '%s/%s' % (path, screenName)
    DEVICE.screenshot(screenPath)
    return Image.open(screenPath), screenPath


def crop(name):
    imgPrefix = 'resource/%s/%s' % (ACT_MODE, name)
    Image.open(
        imgPrefix + '.png').crop(RECTS[name]).save(imgPrefix+'_crop.png')


def contain(imgSmall, imgBig, box=None):
    if box is None:
        box = [0, 0, imgBig.size[0], imgBig.size[1]]
    for x in range(box[0], box[2]):
        for y in range(box[1], box[3]):
            cropBig = imgBig.crop(
                (x, y, x+imgSmall.size[0], y+imgSmall.size[1]))
            if compare(imgSmall, cropBig):
                return True
    return False


def compare(img1, img2):
    for x in range(0, img1.size[0]):
        for y in range(0, img1.size[1]):
            p = (x, y)
            if img1.getpixel(p) != img2.getpixel(p):
                return False
    return True


def printTime():
    millis = int(round(time.time() * 1000))
    print millis

if __name__ == '__main__':
    if 'ACT_DEBUG' in os.environ:
        print ACT_MODE
        if sys.argv[1] == 'screen':
            screen('%s.png' % sys.argv[2], 'resource/'+ACT_MODE)
        elif sys.argv[1] == 'crop':
            crop(sys.argv[2])
        elif sys.argv[1] == 'test':
            crop = Crop.instance(sys.argv[2])
            print crop.compare(screen()[0])
        elif sys.argv[1] == 'compare':
            printTime()
            print contain(
                Image.open('resource/stage/level_crop.png'),
                Image.open('resource/stage/level.png'),
                [80, 700, 180, 810])
            printTime()
        sys.exit(0)
    while True:
        Crop.act()
        time.sleep(3)
