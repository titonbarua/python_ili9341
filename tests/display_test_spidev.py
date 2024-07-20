import sys
sys.path.append("../src/")

import sys

from ili9341.ili9341_spidev import Ili9341Spidev
from test_procedures import *


def run_test_procedures():
    lcd = Ili9341Spidev(
        spidev_bus_no=0,
        spidev_device_no=0,
        dcx_pin_id=23,
        rst_pin_id=None,
        spi_clock_hz=25000000,
        spi_data_chunk_size=2048)

    lcd.clear((0xFF, 0xFF, 0xFF))

    test_fullscreen_color_paint(lcd)
    time.sleep(1.0)
    test_draw_corner_boxes(lcd)
    time.sleep(1.0)
    test_draw_random_boxes(lcd)
    time.sleep(1.0)
    test_display_image(lcd)
    time.sleep(10.0)
    test_play_video(lcd)
    test_webcam(lcd)


if __name__ == "__main__":
    run_test_procedures()
