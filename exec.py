#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yangbo
# @Date:   2015-08-04 11:48:39
# @Last Modified by:   Yang Bo
# @Last Modified time: 2015-08-07 22:57:30

import os
import numpy
import time
from PIL import Image
from uiautomator import Device


DEVICE = Device('192.168.57.101:5555')
RECTS = {
    'back': (90, 430, 230, 470),
    'item': (170, 560, 315, 600),
    'continue': (60, 700, 210, 740),
    'start': (50, 730, 180, 770),
    'game': (130, 730, 230, 760),
    'go': (180, 740, 300, 760)
}


def click(name):
    assert name in RECTS
    box = RECTS[name]
    x = int((box[0] + box[2])/2)
    y = int((box[1] + box[3])/2)
    DEVICE.click(x, y)


def compareFile(a, b, box):
    a = a.crop(box)
    for x in range(0, a.size[0]):
        for y in range(0, a.size[1]):
            p = (x, y)
            pa = a.getpixel(p)
            pb = b.getpixel(p)
            if pa != pb:
                return False
    return True


def compare(img, cropName):
    cropImg = Image.open('screen/%s_crop.png' % cropName)
    return compareFile(img, cropImg, RECTS[cropName])


def crop(imgName):
    assert imgName in RECTS
    box = RECTS[imgName]
    imgPath = 'screen/%s.png' % imgName
    imgSrc = Image.open(imgPath).crop(box)
    imgCropPath = 'screen/%s_crop.png' % imgName
    Image.fromarray(numpy.array(imgSrc)).save(imgCropPath)


def action():
    img, imgPath = screen()
    isItem = False
    for n, box in RECTS.items():
        if compare(img, n):
            print 'found %s' % n
            isItem = n in ['item', 'continue']
            click(n)
            break
    if not isItem:
        os.remove(imgPath)


def printTime():
    import time
    millis = int(round(time.time() * 1000))
    print millis


def screen(screenName=None, path='imgs'):
    if screenName is None:
        screenName = time.strftime('%m_%d_%H_%M_%S.png', time.localtime())
    screenPath = '%s/%s' % (path, screenName)
    DEVICE.screenshot(screenPath)
    return Image.open(screenPath), screenPath


def run():
    while True:
        action()
        time.sleep(3)


if __name__ == '__main__':
    run()
