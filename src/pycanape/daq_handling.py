import math
import time
from threading import Thread, Lock
from typing import List, Dict

from .ecu_task import EcuTask, Sample


class FifoReader:
    def __init__(
        self,
        task: EcuTask,
        channel_list: List[str],
        polling_rate: int,
        save_to_file: bool,
    ):
        self._task = task

        self._setup_daq_channels(channel_list, polling_rate, save_to_file)
        self._channels: Dict[str, Sample] = {channel: None for channel in channel_list}
        self._count = len(self._channels)

        self._thread = Thread(target=self._read_fifo)
        self._lock = Lock()
        self.stopped = True
        self.refresh_rate = 0.001  # seconds

    def _setup_daq_channels(
        self, channel_list: List[str], polling_rate: int, save_to_file: bool
    ):
        for channel_name in channel_list:
            self._task.daq_setup_channel(channel_name, polling_rate, save_to_file)

    @property
    def channel_names(self) -> List[str]:
        return list(self._channels)

    @property
    def task(self) -> EcuTask:
        return self._task

    def start(self):
        self.stopped = False
        self._thread.start()

    def _read_fifo(self):
        self._task.daq_check_overrun(reset_overrun=True)

        while not self.stopped:
            self._task.daq_check_overrun()
            for i in range(self._task.daq_get_fifo_level()):
                samples = self._task.daq_get_next_sample(self._count)

                self._lock.acquire()
                for j, channel_name in enumerate(self._channels):
                    if not math.isnan(samples[j].value):
                        self._channels[channel_name] = samples[j]
                self._lock.release()

            time.sleep(self.refresh_rate)

    def stop(self):
        self.stopped = True
        self._thread.join()

    def get_sample(self, channel_name: str) -> Sample:
        self._lock.acquire()
        sample = self._channels[channel_name]
        self._lock.release()

        return sample

    def get_value(self, channel_name: str) -> float:
        self._lock.acquire()
        sample = self._channels[channel_name]
        self._lock.release()

        return sample.value
