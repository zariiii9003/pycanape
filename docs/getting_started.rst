Getting Started
---------------

Prerequisites
=============

To use pyCANape you need

* Vector CANape 17 or newer installed on your PC
* a valid CANape license
* an existing CANape project
* the location of `CANapAPI.dll` to be appended to your systems `PATH` environment variable.
  The `CANapAPI.dll` is part of your CANape installation.


Installation
============
You can install pyCANape with::

    pip install pycanape


Example
=======

.. code-block::

    import pycanape

    canape = pycanape.CANape(
        project_path="C:\\Users\\Public\\Documents\\Vector CANape 17\\Examples\\XCPDemo",
        modal_mode=True,
        clear_device_list=False,
    )

    # Get XCPsim module
    xcpsim = canape.get_module_by_name("XCPSim")

    # get scalar (0D) calibration object
    scalar_obj = xcpsim.get_calibration_object("map1Counter")

    # read scalar value
    print(scalar_obj.value)

    # set scalar value
    scalar_obj.value = 2.0

    canape.exit(close_canape=True)
