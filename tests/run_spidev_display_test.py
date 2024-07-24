import sys
sys.path.append("../src/")

import time

from ili9341.ili9341_spidev import Ili9341Spidev
import test_procedures as tp


CIRCUIT_GUIDE = """
# ----------------------------------------------------------------,
[RPi2B Compat. Host]   <---> [Display]
==================================================================
Pin-19/GPIO-10/MOSI    <---> MOSI (Main-Out-Sub-In)
Pin-23/GPIO-11/SCLK    <---> SCLK (SPI-Clock)
Pin-24/GPIO-8/SPI0-CE0 <---> CS/X (SPI-Chip-Select)
Pin-22/GPIO-25         <---> DC/X (Data/Control Select for ILI9341)
3.3V+                  <---> RST (We are not using reset pin)
3.3V+                  <---> LED (No software illumination control)
# ----------------------------------------------------------------'
"""

HW_CONFIGS = {
    "rpi3": {
        "spidev_device_path": "/dev/spidev0.0",
        "gpiod_device_path": "/dev/gpiochip0",
        "dcx_pin_id": 25,
        "rst_pin_id": None,
        "spi_clock_hz": 42_000_000,
        "spi_data_chunk_size": 0,  # No chunking!
        "circuit_guide": CIRCUIT_GUIDE,
    },

    "rpi5": {
        "spidev_device_path": "/dev/spidev0.0",
        "gpiod_device_path": "/dev/gpiochip4",
        "dcx_pin_id": 25,
        "rst_pin_id": None,
        "spi_clock_hz": 42_000_000,
        "spi_data_chunk_size": 0,  # No chunking!
        "circuit_guide": CIRCUIT_GUIDE,
    },

    "rpi5-chunked": {
        "spidev_device_path": "/dev/spidev0.0",
        "gpiod_device_path": "/dev/gpiochip4",
        "dcx_pin_id": 25,
        "rst_pin_id": None,
        "spi_clock_hz": 42_000_000,
        "spi_data_chunk_size": 2048,
        "circuit_guide": CIRCUIT_GUIDE,
    },

    "up-squared-v2": {
        "spidev_device_path": "/dev/spidev2.0",
        "gpiod_device_path": "/dev/gpiochip5",
        "dcx_pin_id": 25,
        "rst_pin_id": None,
        # Up squared v2 has a bug where SPI speed does not go over 1MHz.
        # Seems like there is no way around it.
        # Ref: https://forum.up-community.org/discussion/5032/spi-speed-on-up-squared-6000-does-not-go-over-1mhz
        "spi_clock_hz": 20_000_000,
        "spi_data_chunk_size": 0,
        "circuit_guide": CIRCUIT_GUIDE,
    }
}


def run_test_procedures(config_name):
    print(f"Starting Ili9341Spidev display test using config '{config_name}' ...")
    c = HW_CONFIGS[config_name]

    print(c["circuit_guide"])
    lcd = Ili9341Spidev(
        spidev_device_path=c["spidev_device_path"],
        gpiod_device_path=c["gpiod_device_path"],
        dcx_pin_id=c["dcx_pin_id"],
        rst_pin_id=c["rst_pin_id"],
        spi_clock_hz=c["spi_clock_hz"],
        spi_data_chunk_size=c["spi_data_chunk_size"])

    lcd.clear((0xFF, 0xFF, 0xFF))

    tp.test_fullscreen_color_paint(lcd)
    time.sleep(1.0)
    tp.test_draw_corner_boxes(lcd)
    time.sleep(1.0)
    tp.test_draw_random_boxes(lcd)
    time.sleep(1.0)
    tp.test_display_image(lcd)
    time.sleep(10.0)
    tp.test_play_video(lcd)
    tp.test_webcam(lcd)


USAGE = (
    "python3 run_spidev_display_test.py {}"
    .format("|".join(HW_CONFIGS.keys)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    config_name = sys.argv[1]
    if config_name not in HW_CONFIGS:
        print(USAGE)
        sys.exit(2)

    run_test_procedures(config_name)
