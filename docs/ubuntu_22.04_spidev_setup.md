# Setup spidev and gpiod in Ubuntu 22.04

## Installation

- Install `gpiod`, `python3` and `python3-pip` with system package manager:
```
sudo apt install gpiod python3 python3-pip
```
- Both `/dev/spidevX.X` and `/dev/gpiochipY` devices are accessible by group `dialout`.
  To add current user to that group, run -
```
usermod -a -G dialout $USER
```
- Restart the system for group membership to take effect. To make it effective
  without restarting you can use `newgrp dialout`.
- Install the python requirements:
```
pip3 install -r spidev_requirements.txt
pip3 install -r test_requirements.txt
```

## Running tests

```
cd tests/
python3 run_spidev_display_test.py rpi3
```
