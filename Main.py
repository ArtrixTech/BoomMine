import time
import mouseOperation
import random

import imageProcess
import cv2


class BoomMine:
    __inited = False
    blocks_x, blocks_y = -1, -1
    width, height = -1, -1
    img_cv, img = -1, -1
    blocks_img = [[-1 for i in range(blocks_y)] for i in range(blocks_x)]
    blocks_num = [[-3 for i in range(blocks_y)] for i in range(blocks_x)]
    blocks_is_mine = [[0 for i in range(blocks_y)] for i in range(blocks_x)]

    is_new_start = True

    next_steps = []

    @staticmethod
    def rgb_to_bgr(rgb):
        return rgb[2], rgb[1], rgb[0]

    @staticmethod
    def equal(arr1, arr2):
        if arr1[0] == arr2[0] and arr1[1] == arr2[1] and arr1[2] == arr2[2]:
            return True
        return False

    def is_in_form(self, location):
        x, y = location[0], location[1]
        if x < self.left or x > self.right or y < self.top or y > self.bottom:
            return False
        return True

    def iterate_blocks_image(self, func):
        if self.__inited:
            for y in range(self.blocks_y):
                for x in range(self.blocks_x):
                    # args are: self, [0]singleBlockImage, [1]location(as an array)
                    func(self, self.blocks_img[x][y], (x, y))

    def iterate_blocks_number(self, func):
        if self.__inited:
            for y in range(self.blocks_y):
                for x in range(self.blocks_x):
                    # args are: self, [0]singleBlockNumber, [1]location(as an array)
                    func(self, self.blocks_num[x][y], (x, y))

    def analyze_block(self, block, location):
        block = imageProcess.pil_to_cv(block)

        block_color = block[8, 8]
        x, y = location[0], location[1]

        # -1:Not opened
        # -2:Opened but blank
        # -3:Un initialized

        # Opened
        if self.equal(block_color, self.rgb_to_bgr((192, 192, 192))):
            if not self.equal(block[8, 1], self.rgb_to_bgr((255, 255, 255))):
                self.blocks_num[x][y] = -2
                self.is_started = True
            else:
                self.blocks_num[x][y] = -1

        elif self.equal(block_color, self.rgb_to_bgr((0, 0, 255))):
            self.blocks_num[x][y] = 1

        elif self.equal(block_color, self.rgb_to_bgr((0, 128, 0))):
            self.blocks_num[x][y] = 2

        elif self.equal(block_color, self.rgb_to_bgr((255, 0, 0))):
            self.blocks_num[x][y] = 3

        elif self.equal(block_color, self.rgb_to_bgr((0, 0, 128))):
            self.blocks_num[x][y] = 4

        elif self.equal(block_color, self.rgb_to_bgr((128, 0, 0))):
            self.blocks_num[x][y] = 5

        elif self.equal(block_color, self.rgb_to_bgr((0, 128, 128))):
            self.blocks_num[x][y] = 6

        elif self.equal(block_color, self.rgb_to_bgr((0, 0, 0))):
            if self.equal(block[6, 6], self.rgb_to_bgr((255, 255, 255))):
                # Is mine
                self.blocks_num[x][y] = 9
            elif self.equal(block[5, 8], self.rgb_to_bgr((255, 0, 0))):
                # Is flag
                self.blocks_num[x][y] = 0
            else:
                self.blocks_num[x][y] = 7

        elif self.equal(block_color, self.rgb_to_bgr((128, 128, 128))):
            self.blocks_num[x][y] = 8
        else:
            self.blocks_num[x][y] = -3
            self.is_mine_form = False

        if self.blocks_num[x][y] == -3 or not self.blocks_num[x][y] == -1:
            self.is_new_start = False

    def detect_mine(self, block, location):

        def generate_kernel(k, k_width, k_height, block_location):
            ls = []
            loc_x, loc_y = block_location[0], block_location[1]
            for now_y in range(k_height):
                for now_x in range(k_width):

                    if k[now_y][now_x]:
                        rel_x, rel_y = now_x - 1, now_y - 1
                        ls.append((loc_y + rel_y, loc_x + rel_x))
            return ls

        def count_unopen_blocks(blocks):
            count = 0
            for single_block in blocks:
                if self.blocks_num[single_block[1]][single_block[0]] == -1:
                    count += 1
            return count

        def mark_as_mine(blocks):
            for single_block in blocks:
                if self.blocks_num[single_block[1]][single_block[0]] == -1:
                    self.blocks_is_mine[single_block[1]][single_block[0]] = 1

        x, y = location[0], location[1]

        if self.blocks_num[x][y] > 0:

            kernel_width, kernel_height = 3, 3

            # Kernel mode:[Row][Col]
            kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

            # Left border
            if x == 0:
                for i in range(kernel_height):
                    kernel[i][0] = 0

            # Right border
            if x == self.blocks_x - 1:
                for i in range(kernel_height):
                    kernel[i][kernel_width - 1] = 0

            # Top border
            if y == 0:
                for i in range(kernel_width):
                    kernel[0][i] = 0

            # Bottom border
            if y == self.blocks_y - 1:
                for i in range(kernel_width):
                    kernel[kernel_height - 1][i] = 0

            # Generate the search map
            to_visit = generate_kernel(kernel, kernel_width, kernel_height, location)

            unopen_blocks = count_unopen_blocks(to_visit)
            if unopen_blocks == self.blocks_num[x][y]:
                mark_as_mine(to_visit)

    def detect_to_click_block(self, block, location):

        def generate_kernel(k, k_width, k_height, block_location):
            ls = []
            loc_x, loc_y = block_location[0], block_location[1]
            for now_y in range(k_height):
                for now_x in range(k_width):

                    if k[now_y][now_x]:
                        rel_x, rel_y = now_x - 1, now_y - 1
                        ls.append((loc_y + rel_y, loc_x + rel_x))
            return ls

        def count_mines(blocks):
            count = 0
            for single_block in blocks:
                if self.blocks_is_mine[single_block[1]][single_block[0]] == 1:
                    count += 1
            return count

        def mark_to_click_block(blocks):
            for single_block in blocks:

                # Not Mine
                if not self.blocks_is_mine[single_block[1]][single_block[0]] == 1:

                    # Click-able
                    if self.blocks_num[single_block[1]][single_block[0]] == -1:

                        # Source Syntax: [y][x] - Converted
                        if not (single_block[1], single_block[0]) in self.next_steps:
                            self.next_steps.append((single_block[1], single_block[0]))

        x, y = location[0], location[1]

        if block > 0:

            kernel_width, kernel_height = 3, 3

            # Kernel mode:[Row][Col]
            kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

            # Left border
            if x == 0:
                for i in range(kernel_height):
                    kernel[i][0] = 0

            # Right border
            if x == self.blocks_x - 1:
                for i in range(kernel_height):
                    kernel[i][kernel_width - 1] = 0

            # Top border
            if y == 0:
                for i in range(kernel_width):
                    kernel[0][i] = 0

            # Bottom border
            if y == self.blocks_y - 1:
                for i in range(kernel_width):
                    kernel[kernel_height - 1][i] = 0

            # Generate the search map
            to_visit = generate_kernel(kernel, kernel_width, kernel_height, location)

            mines_count = count_mines(to_visit)

            if mines_count == block:
                mark_to_click_block(to_visit)

    def rel_loc_to_real(self, block_rel_location):
        return self.left + 16 * block_rel_location[0] + 8, self.top + 16 * block_rel_location[1] + 8

    def __init__(self):
        self.next_steps = []
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.continue_random_click = False
        self.is_mine_form = True
        self.is_started = False
        self.have_solve = False
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

    def show_mine(self):
        if self.__inited:
            for y in range(self.blocks_y):
                line = ""
                for x in range(self.blocks_x):
                    if self.blocks_is_mine[x][y] == 0:
                        line += "  "
                    else:
                        line += str(self.blocks_is_mine[x][y]) + " "
                print(line)

    def process_once(self):

        # Initialize
        self.img, self.blocks_img, form_size, img_size, form_location = imageProcess.get_frame()
        self.blocks_num = [[-1 for i in range(self.blocks_y)] for i in range(self.blocks_x)]
        self.blocks_is_mine = [[0 for i in range(self.blocks_y)] for i in range(self.blocks_x)]
        self.next_steps = []
        self.is_new_start = True
        self.is_mine_form = True

        if self.img == -1:
            return False

        self.blocks_x, self.blocks_y = form_size[0], form_size[1]
        self.width, self.height = img_size[0], img_size[1]
        self.img_cv = imageProcess.pil_to_cv(self.img)
        self.left, self.top, self.right, self.bottom = form_location

        # Analyze the number of blocks
        self.iterate_blocks_image(BoomMine.analyze_block)

        # Mark all mines
        self.iterate_blocks_number(BoomMine.detect_mine)

        # Calculate where to click
        self.iterate_blocks_number(BoomMine.detect_to_click_block)

        self.have_solve = False
        if len(self.next_steps) > 0:
            self.have_solve = True

        if self.is_in_form(mouseOperation.get_mouse_point()):
            for to_click in self.next_steps:
                on_screen_location = self.rel_loc_to_real(to_click)
                mouseOperation.mouse_move(on_screen_location[0], on_screen_location[1])
                mouseOperation.mouse_click()
                # time.sleep(0.001)

        if not self.have_solve and self.is_mine_form:

            rand_location = (random.randint(0, self.blocks_x - 1), random.randint(0, self.blocks_y - 1))
            rand_x, rand_y = rand_location[0], rand_location[1]
            iter_times = 0

            if len(self.blocks_is_mine) > 0:

                while self.blocks_is_mine[rand_x][rand_y] or not self.blocks_num[rand_x][
                                                                     rand_y] == -1 and iter_times < 20:
                    rand_location = (random.randint(0, self.blocks_x - 1), random.randint(0, self.blocks_y - 1))
                    rand_x, rand_y = rand_location[0], rand_location[1]
                    iter_times += 1

            screen_location = self.rel_loc_to_real((rand_location[0], rand_location[1]))
            if self.is_in_form(mouseOperation.get_mouse_point()):
                mouseOperation.mouse_move(screen_location[0], screen_location[1])
                mouseOperation.mouse_click()
            else:
                self.is_mine_form = False

        cv2.imshow("Sweeper Screenshot", self.img_cv)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        return True


miner = BoomMine()

while 1:
    miner.process_once()
    # miner.show_map()
    # miner.show_mine()
    # print(miner.next_steps)
    # print(miner.blocks_is_mine)
    # time.sleep(0.5)
