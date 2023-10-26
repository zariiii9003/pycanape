# pyCANape

[![PyPI - Version](https://img.shields.io/pypi/v/pycanape.svg)](https://pypi.org/project/pycanape)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pycanape.svg)](https://pypi.org/project/pycanape)
[![Documentation Status](https://readthedocs.org/projects/pycanape/badge/?version=latest)](https://pycanape.readthedocs.io/en/latest/?badge=latest)

This is a pythonic wrapper around the VECTOR CANape API.
The documentation is available [here](https://pycanape.readthedocs.io/en/latest).

## Example usage

### Open and close CANape
````python
import pycanape

canape = pycanape.CANape(
    project_path="C:\\Users\\Public\\Documents\\Vector CANape 17\\Examples\\XCPDemo",
    modal_mode=True,
)
canape.exit(close_canape=True)
````

### Create Module
````python
from pycanape import DriverType, Channels

# Create XCPsim module
xcpsim = canape.create_module(
    module_name="XCPSim",
    database_filename=r"C:\Users\Public\Documents\Vector CANape 17\Examples\XCPDemo\XCPsim.a2l",
    driver=DriverType.ASAP3_DRIVER_XCP,
    channel=Channels.DEV_CAN1,
    go_online=True,
)
````

### Calibration
````python
# get scalar (0D) calibration object
scalar_obj = xcpsim.get_calibration_object("map1Counter")

# read scalar value
print(scalar_obj.value)

# set scalar value
scalar_obj.value = 2.0

# get axis (1D) calibration object
axis_obj = xcpsim.get_calibration_object("Curve1")

# read axis length
axis_dim = axis_obj.dimension

# read axis values
print(axis_obj.axis)

# set axis values
axis_obj.axis = [0] * axis_dim
````

## How to contribute

Setup your development environment:
```shell script
# clone the repository
git clone https://github.com/zariiii9003/pycanape.git

# install pyCANape in editable mode with all development dependencies
pip install -e .[dev,doc]

# install the pre-commit hook
pre-commit install
```

After you implement your changes you should run the static code analysis and check the documentation:
```shell script
# format the code with black
black .

# run the linter
ruff check --fix src

# run the type checker
mypy .

# run the tests
python -m pytest

# build the documentation
python -m sphinx -Wan --keep-going docs build
```