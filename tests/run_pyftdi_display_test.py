import sys
sys.path.append("../src/")

import time

from ili9341.ili9341_pyftdi import Ili9341Pyftdi
import test_procedures as tp


CIRCUIT_GUIDE = """
# ----------------------------------------------------------------,
[FT232H] <---> [Display]
===================-===============================================
D0       <---> SCLK (SPI-Clock)
D1       <---> MOSI (Main-Out-Sub-In)
D3       <---> CS/X (SPI-Chip-Select)
D4       <---> DC/X (Data/Control Select for ILI9341)
3.3V+    <---> RST (We are not using reset pin)
3.3V+    <---> LED (No software illumination control)
# ----------------------------------------------------------------'
"""

HW_CONFIGS = {
    "ft232h": {
        "pyftdi_interface_path": "ftdi://ftdi:232h/1",
        "dcx_pin_id": 4,
        "rst_pin_id": None,
        "spi_clock_hz": 42_000_000,
        "spi_data_chunk_size": 4096,
        "circuit_guide": CIRCUIT_GUIDE,
    },
}


def run_test_procedures(config_name):
    print(f"Starting Ili9341Pyftdi display test using config '{config_name}' ...")
    c = HW_CONFIGS[config_name]

    print(c["circuit_guide"])
    lcd = Ili9341Pyftdi(
        pyftdi_interface_path=c["pyftdi_interface_path"],
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
    "python3 run_pyftdi_display_test.py {}"
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
