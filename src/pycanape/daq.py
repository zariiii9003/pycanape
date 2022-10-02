import math
import time
from threading import Thread, Lock
from typing import List, Dict, Optional

from .ecu_task import EcuTask, Sample
from .utils import CANapeError
from .cnp_api.cnp_constants import ErrorCodes, EventCode
from .canape import CANape


class FifoReader:
    def __init__(
        self, canape_instance: CANape, task: EcuTask, refresh_rate: float
    ) -> None:
        """

        :param canape_instance:
        :param task:
        :param refresh_rate:
        """
        self._task = task
        self.refresh_rate = refresh_rate

        # register callbacks
        self._canape = canape_instance
        self._canape.register_callback(
            event_code=EventCode.et_ON_DATA_ACQ_START, callback_func=self._start
        )
        self._canape.register_callback(
            event_code=EventCode.et_ON_DATA_ACQ_STOP, callback_func=self._stop
        )

        self._channels: Dict[str, Sample] = {}
        self._count = 0

        self._thread: Optional[Thread] = None
        self._lock = Lock()
        self.stopped = True

    def add_channel(
        self, channel_name: str, polling_rate: int, save_to_file: bool
    ) -> None:
        self._lock.acquire()
        if channel_name not in self._channels:
            self._task.daq_setup_channel(channel_name, polling_rate, save_to_file)
            self._channels[channel_name] = Sample(math.nan, math.nan)
            self._count = len(self._channels)
        self._lock.release()

    def clear_channels(self) -> None:
        self._lock.acquire()
        self._channels.clear()
        self._count = len(self._channels)
        self._lock.release()

    @property
    def channel_names(self) -> List[str]:
        self._lock.acquire()
        names = list(self._channels)
        self._lock.release()
        return names

    @property
    def task(self) -> EcuTask:
        return self._task

    def _start(self) -> None:
        self._stop()
        self.stopped = False
        self._thread = Thread(target=self._read_fifo)
        self._thread.start()

    def _stop(self) -> None:
        self.stopped = True
        if self._thread is not None:
            if self._thread.is_alive():
                self._thread.join()
            self._thread = None

    def _read_fifo(self) -> None:
        self._task.daq_check_overrun(reset_overrun=True)

        while not self.stopped:
            self._lock.acquire()

            try:
                self._task.daq_check_overrun()
                for i in range(self._task.daq_get_fifo_level()):
                    samples = self._task.daq_get_next_sample(self._count)

                    for j, channel_name in enumerate(self._channels):
                        if not math.isnan(samples[j].value):
                            self._channels[channel_name] = samples[j]

            except CANapeError as e:
                if e.error_code == ErrorCodes.AEC_NO_VALUES_SAMPLED:
                    pass
                else:
                    raise e

            finally:
                self._lock.release()

            time.sleep(self.refresh_rate)

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

    def __del__(self) -> None:
        self._stop()
        self._canape.unregister_callback(
            event_code=EventCode.et_ON_DATA_ACQ_START, callback_func=self._start
        )
        self._canape.unregister_callback(
            event_code=EventCode.et_ON_DATA_ACQ_STOP, callback_func=self._stop
        )
