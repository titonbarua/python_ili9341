# Mraa based ILI9341 LCD Display driver in Python

This library implements a pure python driver for spi-connected ILI9341 LCD
display, using `mraa` GPIO library. It takes inspiration from
`Adafruit_Python_ILI9341` project. Most constants and some of the timing
values are copied as is. The focus is to display arbitrary image in the
display and increase SPI bandwidth-limited framerate by doing automatic
partial update.


## Usage example:

```python
from mraa_ili9341 import MraaIli9341

# Pins are for Raspberry Pi 3B+
lcd = MraaIli9341(
    spi_id=0, # Spi device.
    dcx_pin_id=3, # DS pin.
    rst_pin_id=5, # RESET pin.
    spi_clock_hz=25000000,
    spi_data_chunk_size=2048)

# Clear the screen to white.
lcd.clear((0xFF, 0xFF, 0xFF))

# Draw a red rectangle.
lcd.framebuff[10:20, 10:40, :] = (0xFF, 0, 0)
lcd.update()
```
