.. pyCANape documentation master file, created by
   sphinx-quickstart on Sun Oct  2 15:18:28 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyCANape
========

.. only:: html

   .. image:: https://img.shields.io/pypi/v/pycanape.svg
       :target: https://pypi.org/project/pycanape
       :alt: PyPI - Version
   .. image:: https://img.shields.io/pypi/pyversions/pycanape.svg
       :target: https://pypi.org/project/pycanape
       :alt: PyPI - Python Version
   .. image:: https://readthedocs.org/projects/pycanape/badge/?version=latest
       :target: https://pycanape.readthedocs.io/en/latest/?badge=latest
       :alt: Documentation Status

.. toctree::
   :maxdepth: 2

   self
   getting_started
   api

Description
-----------

pyCANape is a pythonic wrapper around the VECTOR CANape API.

With pyCANape you can:

* open existing CANape projects::

   canape = pycanape.CANape(
       project_path=r"C:\Users\Public\Documents\Vector CANape 17\Examples\XCPDemo",
       modal_mode=True,
       clear_device_list=False,
   )

* load CANape configurations::

   canape.load_cna_file(
       cna_file=r"C:\Users\Public\Documents\Vector CANape 17\Examples\XCPDemoXCPsimDemo.cna"
   )

* connect and disconnect devices::

   xcpsim = canape.get_module_by_name("XCPSim")
   xcpsim.switch_ecu_on_offline(online=True)

* start/stop data acquisition::

   canape.start_data_acquisition()
   canape.stop_data_acquisition()

* define and start/stop recorders::

   recorder = canape.get_selected_recorder()
   recorder.set_mdf_filename(filename="test.mf4")
   recorder.start()
   recorder.stop()

* get/set ECU variables::

   map1_counter = xcpsim.get_calibration_object("map1Counter")
   old_value = map1_counter.value
   map1_counter.value = 0

