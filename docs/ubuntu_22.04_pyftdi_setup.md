# Setup pyftdi in Ubuntu 22.04

## Installation

- Install `libusb` using system package manager:
```
sudo apt-get install libusb-1.0-0
```
- Install python requirements:
```
pip3 install -r pyftdi_requirements.txt
pip3 install -r test_requirements.txt
```

## Running tests

```
cd tests/
python3 run_pyftdi_display_test.py rpi3
```
