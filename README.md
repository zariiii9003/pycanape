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
import subprocess

import pycanape
from pycanape import DriverType, Channels

# start new XCPsim ECU simulator
sim_process = subprocess.Popen(
    "C:\\Users\\Public\\Documents\\Vector CANape 17\\Examples\\_Simulators\\XCPSim\\xcpsim.exe"
)

# Start CANape
canape = pycanape.CANape(
    project_path="C:\\Users\\Public\\Documents\\Vector CANape 17\\Examples\\XCPDemo"
)

# Create XCPsim module
xcpsim_module = canape.create_module(
    module_name="XCPSim",
    database_filename=r"C:\Users\Public\Documents\Vector CANape 17\Examples\XCPDemo\XCPsim.a2l",
    driver=DriverType.ASAP3_DRIVER_XCP,
    channel=Channels.DEV_CAN1,
    go_online=True,
)

# Close CANape
canape.exit(close_canape=True)

# stop XCPsim ECU simulator
sim_process.kill()
````
