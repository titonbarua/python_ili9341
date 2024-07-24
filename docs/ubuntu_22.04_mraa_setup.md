# Setup MRAA library in Ubuntu 22.04

## Installation

The most straight forward and hassle free way to install mraa library is
to compile it from source. Here's the step by step procedure for installing
it in Ubuntu 22.04:

- Clone mraa from github:

```sh
cd ~
git clone https://github.com/eclipse/mraa.git
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
- Check the gpio pins are properly recognized with the command `mraa-gpio list`.
  Open a python shell with `python3` and type in `import mraa`. If everything
  goes well, there should be no error.
- Install python requirements using:
```
pip3 install -r mraa_requirements.txt
pip3 install -r test_requirements.txt
```

## Running tests

```
cd tests/
python3 run_mraa_display_test.py rpi3
```
Mraa seems like an abandoned project. In my tests, Mraa was able to recognize
gpio pins only on RPi3 B+. The library seems to use `sysfs` interfaces for
`spi` and `gpio` access, some of which are deprecated in modern Linux.

If the tests fail with `ValueError: Invalid GPIO pin specified.`, it means the
sysfs gpio pins have not been properly exported. The best practice is to look at
the sysfs numbers of required pins and then export and change permissions for
specific pins. The lazy way is to run your program as root:

```
sudo apt install python3-opencv python3-numpy
sudo python3 run_mraa_display_test.py rpi3
```
