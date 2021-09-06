# pyCANape

This is a pythonic wrapper around the VECTOR CANape API.

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