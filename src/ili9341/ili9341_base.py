"""
This module implements a pure python driver for spi-connected ILI9341 LCD display.
"""

import numpy as np
import math
import time

# Constants for interacting with display registers.
ILI9341_TFTWIDTH    = 320
ILI9341_TFTHEIGHT   = 240

ILI9341_NOP         = 0x00
ILI9341_SWRESET     = 0x01
ILI9341_RDDID       = 0x04
ILI9341_RDDST       = 0x09

ILI9341_SLPIN       = 0x10
ILI9341_SLPOUT      = 0x11
ILI9341_PTLON       = 0x12
ILI9341_NORON       = 0x13

ILI9341_RDMODE      = 0x0A
ILI9341_RDMADCTL    = 0x0B
ILI9341_RDPIXFMT    = 0x0C
ILI9341_RDIMGFMT    = 0x0A
ILI9341_RDSELFDIAG  = 0x0F

ILI9341_INVOFF      = 0x20
ILI9341_INVON       = 0x21
ILI9341_GAMMASET    = 0x26
ILI9341_DISPOFF     = 0x28
ILI9341_DISPON      = 0x29

ILI9341_CASET       = 0x2A
ILI9341_PASET       = 0x2B
ILI9341_RAMWR       = 0x2C
ILI9341_RAMRD       = 0x2E

ILI9341_PTLAR       = 0x30
ILI9341_MADCTL      = 0x36
ILI9341_PIXFMT      = 0x3A

# Memory access contrl (MADCTL) flags.
ILI9341_MADCTL_ROW_ACCESS_REVERSED = 1 << 7
ILI9341_MADCTL_COL_ACCESS_REVERSED = 1 << 6
ILI9341_MADCTL_ROW_COL_EXCHANGE = 1 << 5
ILI9341_MADCTL_VERT_REFRESH_REVERSED = 1 << 4
ILI9341_MADCTL_BGR_MODE = 1 << 3
ILI9341_MADCTL_HORZ_REFRESH_REVERSED = 1 << 2

ILI9341_FRMCTR1     = 0xB1
ILI9341_FRMCTR2     = 0xB2
ILI9341_FRMCTR3     = 0xB3
ILI9341_INVCTR      = 0xB4
ILI9341_DFUNCTR     = 0xB6

ILI9341_PWCTR1      = 0xC0
ILI9341_PWCTR2      = 0xC1
ILI9341_PWCTR3      = 0xC2
ILI9341_PWCTR4      = 0xC3
ILI9341_PWCTR5      = 0xC4
ILI9341_VMCTR1      = 0xC5
ILI9341_VMCTR2      = 0xC7

ILI9341_RDID1       = 0xDA
ILI9341_RDID2       = 0xDB
ILI9341_RDID3       = 0xDC
ILI9341_RDID4       = 0xDD

ILI9341_GMCTRP1     = 0xE0
ILI9341_GMCTRN1     = 0xE1

ILI9341_PWCTR6      = 0xFC

ILI9341_BLACK       = 0x0000
ILI9341_BLUE        = 0x001F
ILI9341_RED         = 0xF800
ILI9341_GREEN       = 0x07E0
ILI9341_CYAN        = 0x07FF
ILI9341_MAGENTA     = 0xF81F
ILI9341_YELLOW      = 0xFFE0
ILI9341_WHITE       = 0xFFFF


class Ili9341Base(object):
    """IO library agnostic base class for controlling ILI9341 SPI displays."""

    def __init__(
            self,
            spi_data_chunk_size=2048,
            partial_update_merge_dist=5,
            madctl_cmd_val=ILI9341_MADCTL_BGR_MODE):
        """Initialize Ili9341Base class.

        Args:

        - spi_data_chunk_size: (int) Size of the each SPI data transaction. If
          set to zero, no chunking is used. For some interfaces like Spidev
          have own buffers where no-chunking might be beneficial. pyftdi will
          refuse if large buffers are tried without chunking.

        - partial_update_merge_dist: (int) The distance to look for when
          merging two small partial updates into one.

        - madctl_cmd_val: (int-flags) This is a bitmask that can be used to
          rotate/flip the display image. Look at the ILI9341 datasheet for
          more.

        """
        self._height = ILI9341_TFTHEIGHT
        self._width = ILI9341_TFTWIDTH
        self._spi_data_chunk_size = spi_data_chunk_size
        self._partial_update_merge_dist = partial_update_merge_dist
        self._madctl_cmd_val = madctl_cmd_val

        self._buffer_shape = (self._height, self._width, 3)

        # The framebuffer to display.
        self._framebuff = np.zeros(self._buffer_shape, dtype=np.uint8)

        # Create an array as a sketch pad for color conversion.
        self._workbuff = np.zeros(self._buffer_shape, dtype=np.uint16)

        self._old_data = None

        self.reset()
        self.init_display()

    @property
    def framebuff(self):
        """A numpy array to hold pixel values.

        User should modify pixel values directly using this. The layout is:
        (<height>, <width>, <rgb-color>)

        """
        return self._framebuff

    @framebuff.setter
    def framebuff(self, new_buff):
        # Convert buffer to an array, if necessary.
        new_buff = np.array(new_buff, dtype=np.uint8).reshape(
            (self._height, self._width, 3))

        self._framebuff = new_buff

    def _spi_write(self, buff):
        raise NotImplementedError

    def _switch_to_ctrl_mode(self):
        raise NotImplementedError

    def _switch_to_data_mode(self):
        raise NotImplementedError

    def _do_hardware_reset(self):
        raise NotImplementedError

    def send_cmd(self, buff):
        """Send a composite command.

        The first byte is assumed to be a command. Rest of the bytes are
        assumed to be data.

        """
        buff = bytearray(buff)

        # Send the command byte.
        self._switch_to_ctrl_mode()
        self._spi_write(buff[:1])

        # Send the data that comes after command in chunks.
        # -----------------------------------------------------,
        self._switch_to_data_mode()
        s = self._spi_data_chunk_size

        if s > 0:
            n_chunks = math.ceil(len(buff[1:]) / s)
            i = 0
            while i < n_chunks:
                self._spi_write(buff[(1 + i * s):(1 + (i + 1) * s)])
                i += 1
        else:
            self._spi_write(buff[1:])
        # -----------------------------------------------------'

    def init_display(self):
        """Initialize the display."""
        init_cmd_list = [
            bytearray([ILI9341_DISPOFF]),
            b"\xEF\x03\x80\x02",
            b"\xCF\x00\xC1\x30",
            b"\xED\x64\x03\x12\x81",
            b"\xE8\x85\x00\x78",
            b"\xCB\x39\x2C\x00\x34\x02",
            b"\xF7\x20",
            b"\xEA\x00\x00",
            bytearray([ILI9341_PWCTR1, 0x23]),
            bytearray([ILI9341_PWCTR2, 0x10]),
            bytearray([ILI9341_VMCTR1, 0x3e, 0x28]),
            bytearray([ILI9341_VMCTR2, 0x86]),
            # bytearray([ILI9341_MADCTL, 0x84]),
            bytearray([ILI9341_MADCTL, self._madctl_cmd_val & 0xFF]),

            bytearray([ILI9341_PIXFMT, 0x55]),
            bytearray([ILI9341_FRMCTR1, 0x00, 0x18]),
            bytearray([ILI9341_DFUNCTR, 0x08, 0x82, 0x27]),
            b"\xF2\x00",
            bytearray([ILI9341_GAMMASET, 0x01]),
            bytearray([ILI9341_GMCTRP1, 0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1, 0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00]),
            bytearray([ILI9341_GMCTRN1, 0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1, 0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F]),
            bytearray([ILI9341_PTLON])
        ]

        for cmd in init_cmd_list:
            self.send_cmd(cmd)
            time.sleep(0.01)

        self.send_cmd(bytearray([ILI9341_SLPOUT]))
        time.sleep(0.120)
        self.send_cmd(bytearray([ILI9341_DISPON]))

    def reset(self, soft=True):
        """Reset the display."""
        # Do a hardware reset if possible before a software reset.
        self._do_hardware_reset()
        self.send_cmd(bytearray([ILI9341_SWRESET]))

    def _find_updated_cols(self, top, bot, diff):
        areas = []
        cols = np.where(diff[top:(bot + 1), :].sum(axis=0) > 0)[0]
        for i, curr_col in enumerate(cols):
            prev_col = cols[i - 1] if i > 0 else curr_col
            if i == 0:
                left = right = curr_col

            if i == (len(cols) - 1):
                areas.append((left, top, curr_col, bot))

            elif curr_col >= (prev_col + self._partial_update_merge_dist):
                areas.append((left, top, right, bot))
                left = right = curr_col

            else:
                right = curr_col

            i += 1

        return areas

    def _find_updated_rows(self, diff):
        areas = []
        rows = np.where(diff.sum(axis=1) > 0)[0]
        for i, curr_row in enumerate(rows):
            prev_row = rows[i - 1] if i > 0 else curr_row
            if i == 0:
                top = bot = curr_row

            if i == (len(rows) - 1):
                areas += self._find_updated_cols(top, curr_row, diff)
            elif curr_row >= (prev_row + self._partial_update_merge_dist):
                areas += self._find_updated_cols(top, bot, diff)
                top = bot = curr_row
            else:
                bot = curr_row

            i += 1

        return areas

    def _find_updated_areas(self, old_data, new_data):
        if self._old_data is None:
            return [(0, 0, self._width - 1, self._height - 1)]

        diff = new_data != old_data
        return self._find_updated_rows(diff)

    def _update_partial(self, new_data, x1, y1, x2, y2):
        buff = new_data[
            y1:(y2 + 1), x1:(x2 + 1)].swapaxes(0, 1).byteswap().tobytes(order='C')

        self.send_cmd(bytearray([
            ILI9341_PASET, x1 >> 8, x1 & 0xFF, x2 >> 8, x2 & 0xFF]))
        self.send_cmd(bytearray([
            ILI9341_CASET, y1 >> 8, y1 & 0xFF, y2 >> 8, y2 & 0xFF]))
        self.send_cmd(
            bytearray([ILI9341_RAMWR]) +
            bytearray(buff))

    def update(self):
        """Update display."""
        # Do color conversion to RGB 565 mode in work buffer.
        # --------------------------------------------------,
        # Copy data from frame buffer to workbuffer.
        self._workbuff[:, :, :] = self.framebuff.astype(np.uint16)

        # Prepare red channel.
        self._workbuff[:, :, 0] >>= 3
        self._workbuff[:, :, 0] <<= 11

        # Prepare green channel.
        self._workbuff[:, :, 1] >>= 2
        self._workbuff[:, :, 1] <<= 5

        # Prepare blue channel.
        self._workbuff[:, :, 2] >>= 3

        # Merge all three channels in red buffer.
        self._workbuff[:, :, 0] |= self._workbuff[:, :, 1]
        self._workbuff[:, :, 0] |= self._workbuff[:, :, 2]

        new_data = self._workbuff[:, :, 0]
        # --------------------------------------------------'

        updated_areas = self._find_updated_areas(self._old_data, new_data)
        self._old_data = new_data.copy()
        for area in updated_areas:
            self._update_partial(new_data, *area)

    def clear(self, color=(0, 0, 0)):
        """Clear display with a specific color."""
        self.framebuff[:, :, :] = color
        self.update()
