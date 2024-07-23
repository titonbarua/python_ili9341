"""This module implements a pure python driver for spi-connected ILI9341 LCD
display, using `python-spidev` and `sysfs-gpio` GPIO libraries.

Spidev: https://pypi.org/project/gpio/
Linux sysfs gpio: https://pypi.org/project/gpio/

"""

import re
import time
import spidev
import gpiod
import gpiod.line

from .ili9341_base import Ili9341Base


RX_SPIDEV_DEVICE_NUMS = re.compile(r"/dev/spidev([\d+])\.([\d+])")


class Ili9341Spidev(Ili9341Base):
    """Class to manipulate ILI9341 SPI displays using python-spidev and
    sysfs-gpio libraries.

    """

    def __init__(
            self,
            spidev_device_path,
            gpiod_device_path,
            dcx_pin_id,
            rst_pin_id=None,
            spi_clock_hz=64000000,
            **kwargs):
        """Initialize Ili9341Spidev class."""
        m = RX_SPIDEV_DEVICE_NUMS.match(spidev_device_path)
        if m is None:
            raise ValueError(
                "Spidev device path seems incorrect!"
                " It should be something like: /dev/spidevX.Y")

        # Create SPI device.
        self._spi = spidev.SpiDev()
        spidev_bus_no, spidev_device_no = [
            int(x) for x in m.groups()]
        self._spi.open(spidev_bus_no, spidev_device_no)

        self._spi.mode = 0b00  # SPI mode 0.
        self._spi.lsbfirst = False  # MSB first.
        self._spi.max_speed_hz = spi_clock_hz

        # Create GPIO interface for data/control select line.
        self._gpiod_chip = gpiod.Chip(gpiod_device_path)
        self._dcx_pin_id = dcx_pin_id
        self._rst_pin_id = rst_pin_id

        line_request_config = {
            self._dcx_pin_id: gpiod.LineSettings(
                direction=gpiod.line.Direction.OUTPUT,
                active_low=False
            )
        }

        if self._rst_pin_id is not None:
            line_request_config[self._rst_pin_id] = gpiod.LineSettings(
                direction=gpiod.line.Direction.OUTPUT,
                active_low=True)

        self._line_access = gpiod.request_lines(
            gpiod_device_path,
            consumer="Ili9341Spidev_display_driver",
            config=line_request_config)

        super().__init__(**kwargs)

    def __del__(self):
        """Do cleanup."""
        # Release gpio access.
        self._line_access.release()

    def _spi_write(self, buff):
        self._spi.writebytes2(buff)

    def _switch_to_ctrl_mode(self):
        self._line_access.set_value(
            self._dcx_pin_id,
            gpiod.line.Value.INACTIVE)

    def _switch_to_data_mode(self):
        self._line_access.set_value(
            self._dcx_pin_id,
            gpiod.line.Value.ACTIVE)

    def _do_hardware_reset(self):
        if self._rst_pin_id is not None:
            self._line_access.set_value(
                self._rst_pin_id, gpiod.line.Value.INACTIVE)
            time.sleep(0.005)
            self._line_access.set_value(
                self._rst_pin_id, gpiod.line.Value.ACTIVE)
            time.sleep(0.02)
            self._line_access.set_value(
                self._rst_pin_id, gpiod.line.Value.INACTIVE)
            time.sleep(0.150)
