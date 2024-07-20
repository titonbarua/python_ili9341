"""This module implements a pure python driver for spi-connected ILI9341 LCD
display, using `python-spidev` and `sysfs-gpio` GPIO libraries.

Spidev: https://pypi.org/project/gpio/
Linux sysfs gpio: https://pypi.org/project/gpio/

"""

import time
import spidev
import gpio

from .ili9341_base import Ili9341Base


class Ili9341Spidev(Ili9341Base):
    """Class to manipulate ILI9341 SPI displays using python-spidev and
    sysfs-gpio libraries.

    """

    def __init__(
            self,
            spidev_bus_no,
            spidev_device_no,
            dcx_pin_id,
            rst_pin_id=None,
            spi_clock_hz=64000000,
            **kwargs):
        """Initialize Ili9341Spidev class."""
        # Create SPI device.
        self._spi = spidev.SpiDev()
        self._spi.open(spidev_bus_no, spidev_device_no)

        self._spi.mode = 0b00  # SPI mode 0.
        self._spi.lsbmode = True  # MSB first.
        self._spi.max_speed_hz = spi_clock_hz

        # Create GPIO interface for data/control select line.
        self._dcx_pin = gpio.GPIOPin(dcx_pin_id, gpio.OUT)

        # Create GPIO interface for reset line, if given.
        if rst_pin_id:
            self._rst_pin = gpio.GPIOPin(rst_pin_id, gpio.OUT)
        else:
            self._rst_pin = None

        super().__init__(**kwargs)

    def _spi_write(self, buff):
        self._spi.writebytes2(buff)

    def _switch_to_control_mode(self):
        self._dcx_pin.write(gpio.LOW)

    def _switch_to_data_mode(self):
        self._dcx_pin.write(gpio.HIGH)

    def _do_hardware_reset(self):
        if self._rst_pin is not None:
            self._rst_pin.write(gpio.HIGH)
            time.sleep(0.005)
            self._rst_pin.write(gpio.LOW)
            time.sleep(0.02)
            self._rst_pin.write(gpio.HIGH)
            time.sleep(0.150)
