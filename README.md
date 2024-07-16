# Mraa based ILI9341 LCD display driver in pure python

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

## Installing Intel MRAA library with python bindings

The most straight forward and hassle free way to install mraa library is
to compile it from source. Here's the step by step procedure for installing
it in Ubuntu 22.04:

- Clone mraa from github:

```sh
cd ~
git clone git@github.com:eclipse/mraa.git
```
- Copy build requirements:

```sh
sudo apt update
sudo apt upgrade
sudo apt install git build-essential swig3.0 python3-dev cmake python3-is-python
```
- Configure and build mraa and python binding:

```sh
cd ~/mraa
mkdir build
cd build
cmake .. -DBUILDSWIGNODE=OFF -DBUILDSWIGPYTHON=ON
make
sudo make install
```
- Copy compiled files into proper places manually to fix incompatiblity issues with debian path
  conventions. In the following commands, change `3.XX` with your installed version, say with `3.10`.

```sh
sudo ln -s /usr/local/lib/*mraa.so* /usr/lib/
sudo ln -s /usr/local/lib/python3.XX/dist-packages/*mraa* /usr/lib/python3/dist-packages/
```
- Test if mraa python binding is working. Open a python shell with `python3` and type in `import mraa`.
  If everything goes well, there should be no error.

