"""This module implements a pure python driver for spi-connected ILI9341 LCD
display, using FTxxx family USB-to-GPIO breakout boards.

"""

import re
import time
import pyftdi.spi

from .ili9341_base import Ili9341Base


class Ili9341Pyftdi(Ili9341Base):
    """Class to manipulate ILI9341 SPI displays using FTxxxx (FT232h etc.)
    family USB-to-GPIO breakout boards.

    """

    def __init__(
            self,
            pyftdi_interface_path,
            dcx_pin_id,
            rst_pin_id=None,
            spi_clock_hz=64000000,
            **kwargs):
        """Initialize Ili9341Pyftdi class.

        Args:
        - pyftdi_interface_path: (str) A path describing FTDI io interface. E.g.: 'ftdi://ftdi:232h/1'
        - dcx_pin_id: (int) Pin where display DC/X pin is connected. If it is
                      connected to FT232H's pin 'D4', pin will be `4`.
        - rst_pin_id: (int, optional) Pin where display RST pin is connected.
        - spi_clock_hz: (int) Maximum SPI frequency in Hz supported by the FTDI chip.
        """
        # Create SPI device.
        self._spi_controller = pyftdi.spi.SpiController(cs_count=1)
        self._spi_controller.configure(pyftdi_interface_path)

        self._spi = self._spi_controller.get_port(
            cs=0, freq=spi_clock_hz, mode=0)

        # Configure GPIO.
        self._dcx_pin_id = dcx_pin_id
        self._rst_pin_id = rst_pin_id

        self._gpio = self._spi_controller.get_gpio()
        if self._rst_pin_id is not None:
            self._gpio.set_direction(
                (1 << self._dcx_pin_id) | (1 << self._rst_pin_id),
                (1 << self._dcx_pin_id) | (1 << self._rst_pin_id))
        else:
            self._gpio.set_direction(
                1 << self._dcx_pin_id, 1 << self._dcx_pin_id)

        super().__init__(**kwargs)

    def _spi_write(self, buff):
        self._spi.write(buff)

    def _switch_to_ctrl_mode(self):
        self._gpio.write(0 << self._dcx_pin_id)

    def _switch_to_data_mode(self):
        self._gpio.write(1 << self._dcx_pin_id)

    def _do_hardware_reset(self):
        if self._rst_pin_id is not None:
            self._gpio.write(1 << self._rst_pin_id)
            time.sleep(0.005)
            self._gpio.write(0 << self._rst_pin_id)
            time.sleep(0.02)
            self._gpio.write(1 << self._rst_pin_id)
            time.sleep(0.150)
