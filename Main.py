import win32gui
import win32api
import time

import numpy
from PIL import ImageGrab

import imageProcess
import cv2


class BoomMine:

    __inited = False
    blocks_x, blocks_y = -1, -1
    width, height = -1, -1
    img_cv, img = -1, -1
    blocks_img = [[-1 for i in range(blocks_y)] for i in range(blocks_x)]
    blocks_num = [[-1 for i in range(blocks_y)] for i in range(blocks_x)]

    @staticmethod
    def rgb_to_bgr(rgb):
        return rgb[2], rgb[1], rgb[0]

    @staticmethod
    def equal(arr1, arr2):
        if arr1[0] == arr2[0] and arr1[1] == arr2[1] and arr1[2] == arr2[2]:
            return True
        return False

    def iterate_blocks_image(self, func):

        if self.__inited:
            for y in range(self.blocks_y):
                for x in range(self.blocks_x):
                    # args are: self, [0]singleBlockImage, [1]location(as an array)
                    func(self, self.blocks_img[x][y], (x, y))

    def analyze_block(self, block, location):
        block = imageProcess.pil_to_cv(block)

        block_color = block[8, 8]
        x, y = location[0], location[1]

        if self.equal(block_color, self.rgb_to_bgr((0, 0, 255))):
            self.blocks_num[x][y] = 1

        if self.equal(block_color, self.rgb_to_bgr((0, 128, 0))):
            self.blocks_num[x][y] = 2

        if self.equal(block_color, self.rgb_to_bgr((255, 0, 0))):
            self.blocks_num[x][y] = 3

        if self.equal(block_color, self.rgb_to_bgr((0, 0, 128))):
            self.blocks_num[x][y] = 4

        if self.equal(block_color, self.rgb_to_bgr((128, 0, 0))):
            self.blocks_num[x][y] = 5

        if self.equal(block_color, self.rgb_to_bgr((0, 128, 128))):
            self.blocks_num[x][y] = 6

        if self.equal(block_color, self.rgb_to_bgr((0, 0, 0))):
            self.blocks_num[x][y] = 7

        if self.equal(block_color, self.rgb_to_bgr((128, 128, 128))):
            self.blocks_num[x][y] = 8

    def __init__(self):
        if self.process_once():
            self.__inited = True

    def show_map(self):
        if self.__inited:
            for y in range(self.blocks_y):
                line = ""
                for x in range(self.blocks_x):
                    if self.blocks_num[x][y] == -1:
                        line += "  "
                    else:
                        line += str(self.blocks_num[x][y]) + " "
                print(line)

    def process_once(self):
        self.img, self.blocks_img, size, img_size = imageProcess.get_frame()
        self.blocks_num = [[-1 for i in range(self.blocks_y)] for i in range(self.blocks_x)]

        if self.img == -1:
            return False

        self.blocks_x, self.blocks_y = size[0], size[1]
        self.width, self.height = img_size[0], img_size[1]
        self.img_cv = imageProcess.pil_to_cv(self.img)

        self.iterate_blocks_image(BoomMine.analyze_block)

        cv2.imshow("Sweeper Screenshot", self.img_cv)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        return True


miner = BoomMine()

while 1:
    miner.process_once()
    miner.show_map()
    time.sleep(1)
