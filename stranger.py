import colorsys
import os
import random
import time
from threading import Thread
import logging

from rpi_ws281x import *

from messages import messages

LED_COUNT = 50
GPIO_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 5
LED_BRIGHTNESS = 15
LED_INVERT = False
LED_CHANNEL = 0
LED_STRIP = ws.WS2811_STRIP_RGB  # Strip type and colour ordering

build_iter = 1

CHAR_IDX = {
    'A': 48,
    'B': 47,
    'C': 45,
    'D': 43,
    'E': 42,
    'F': 40,
    'G': 39,
    'H': 37,
    'I': 20,
    'J': 22,
    'K': 24,
    'L': 25,
    'M': 26,
    'N': 27,
    'O': 29,
    'P': 31,
    'Q': 33,
    'R': 14,
    'S': 13,
    'T': 12,
    'U': 10,
    'V': 9,
    'W': 7,
    'X': 5,
    'Y': 3,
    'Z': 1,
    ' ': "NONE",
    '!': "FLASH",
    '*': "CREEP",
    '@': "ALPHABET"
}

strip = Adafruit_NeoPixel(LED_COUNT, GPIO_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()
strip.show()
cancelled = False
level = logging.DEBUG
logging.basicConfig()
logging.getLogger().setLevel(level)

def rand_color():
    return color_of(random.random())


def set_color(led, c):
    strip.setPixelColor(led, Color(*c))


def set_all(color):
    for i in range(0, LED_COUNT):
        set_color(i, color)


def color_of(i):
    """
    This function generates a color based on the index of an LED. This will always return the same color for a given
    index. This allows the lights to function more like normal christmas lights where the color of one bulb wont change.

    :param i: index of LED to get color of
    :return: a pseudorandom color based on the index of the light
    """
    random.seed(i)
    rgb = colorsys.hsv_to_rgb(random.random(), 1, 1)
    return int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)


def set_all_color_of():
    """
    Sets all LEDs to a pseudorandom color, that is the same for each LED every time this function is called
    """
    for i in range(0, LED_COUNT):
        set_color(i, color_of(i))


def creep(start=0, n=50):
    """
    Sequentially illuminates each LED

    :param start: Index to start creeping from
    :param n: Number between 1 and LED_COUNT of lights to creep.
    """
    for i in range(start, n):
        set_color((i-1) % LED_COUNT, (0, 0, 0))
        set_color(i % LED_COUNT, rand_color())
        strip.show()
        time.sleep(1)

def build():
    global build_iter
    clear_all()
    strip.show()
    if build_iter % 2 == 0:
        num_list = range(LED_COUNT, -1, -1)
    else:
        num_list = range(0, LED_COUNT)
    for i in num_list:
        if displaying:
            break
        else:
            new_color = rand_color()
            strip.setPixelColorRGB(i, new_color[0], new_color[1], new_color[2])
            strip.show()
            time.sleep(.3)
    build_iter += 1

def clear_all():
    set_all((0, 0, 0))
    strip.show()

def test_all():
    clear_all()
    for i in range(0, 50):
        print("setting color for {}".format(i))
        set_color(i, (0, 0, 0))
        time.sleep(1)
        set_color(i, (255, 0, 0))
        strip.show()
        time.sleep(2)
        set_color(i, (0, 0, 0))

def flash(n):
    for i in range(0, n):
        set_all_color_of()
        strip.show()
        time.sleep(1)
        set_all((0, 0, 0))
        strip.show()
        time.sleep(.5)

displaying = False


def display(msg):
    global displaying
    displaying = True
    time.sleep(1)
    for c in msg:
        clear_all()
        set_all((0, 0, 0))
        if c.upper() in CHAR_IDX:
            i = CHAR_IDX[c.upper()]
            if i == "NONE":
                "do nothing"
            elif i == "FLASH":
                flash(3)
            elif i == "CREEP":
                creep(50)
            elif i == "ALPHABET":
                alphabet()
            else:
                set_color(i, color_of(i))
            strip.show()
            time.sleep(1)
            clear_all()
            time.sleep(.2)
    time.sleep(1)
    displaying = False


def listen_on_console(prompt):
    print("Enter messages here. To quit, enter \"\\exit\"")
    while True:
        msg = input(prompt)
        if msg == "\\exit":
            os._exit(1)
        display(msg)


def check_for_message():
    print("Enter messages here. To quit, enter \"\\exit\"")
    global displaying
    while True:
        if not displaying:
            msg = messages.next_message()
            print("displaying: ", msg)
            display(msg[:50])
        time.sleep(1)


def clear_errors():
    """
    Sometimes pixels will randomly turn themselves on. This fixes them by resetting the board every 2 seconds
    """
    global displaying
    while True:
        if not displaying:
            clear_all()
            build()
        time.sleep(2)

# borrowed from https://github.com/jgarff/rpi_ws281x/blob/master/python/examples/strandtest.py
def color_wipe(color, wait_ms=800):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def alphabet():
    display("abcdefghijklmnopqrstuvwxyz")


def start_client():
    t0 = Thread(target=listen_on_console, args=("",))
    t1 = Thread(target=check_for_message, args=())
    t2 = Thread(target=clear_errors, args=())

    t0.start()
    t1.start()
    t2.start()
