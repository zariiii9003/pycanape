# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

import ctypes
import sys
import typing

# compatibility fix for python 3.7
if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from backports.cached_property import cached_property

import numpy as np

from . import ObjectType, ValueType, CANapeError, RC
from .cnp_api import cnp_class, cnp_constants

try:
    from .cnp_api import cnp_prototype
except FileNotFoundError:
    cnp_prototype = None  # type: ignore[assignment]

if typing.TYPE_CHECKING:
    import numpy.typing as npt


class BaseCalibrationObject:
    def __init__(
        self,
        asap3_handle: cnp_class.TAsap3Hdl,  # type: ignore[valid-type]
        module_handle: typing.Union[cnp_class.TModulHdl, int],
        name: str,
        object_info: cnp_class.DBObjectInfo,
    ) -> None:
        if cnp_prototype is None:
            raise FileNotFoundError(
                "CANape API not found. Add CANape API location to environment variable `PATH`."
            )

        self._asap3_handle = asap3_handle
        self._module_handle = module_handle
        self._name = name
        self._object_info = object_info
        self._force_upload = True
        try:
            self._datatype: typing.Optional[
                cnp_constants.TAsap3DataType
            ] = self._read_datatype()
        except CANapeError:
            self._datatype = None

    def _read_datatype(self) -> cnp_constants.TAsap3DataType:
        _dtype = cnp_class.enum_type(0)
        _address = ctypes.c_ulong(0)
        _min = ctypes.c_double(0)
        _max = ctypes.c_double(0)
        _increment = ctypes.c_double(0)
        cnp_prototype.Asap3ReadObjectParameter(
            self._asap3_handle,
            self._module_handle,
            self._name.encode(RC["ENCODING"]),
            cnp_constants.TFormat.PHYSICAL_REPRESENTATION,
            ctypes.byref(_dtype),
            ctypes.byref(_address),
            ctypes.byref(_min),
            ctypes.byref(_max),
            ctypes.byref(_increment),
        )
        return cnp_constants.TAsap3DataType(_dtype.value)

    def _read_calibration_object_value(self) -> cnp_class.TCalibrationObjectValue:
        cov = cnp_class.TCalibrationObjectValue()
        cnp_prototype.Asap3ReadCalibrationObject2(
            self._asap3_handle,
            self._module_handle,
            self._name.encode(RC["ENCODING"]),
            cnp_constants.TFormat.PHYSICAL_REPRESENTATION,
            self._force_upload,
            ctypes.byref(cov),
        )
        return cov

    def _write_calibration_object_value(
        self, cov: cnp_class.TCalibrationObjectValue
    ) -> None:
        if self.object_type != ObjectType.OTT_CALIBRATE:
            raise TypeError("Cannot set value to a Measurement Object.")
        cnp_prototype.Asap3WriteCalibrationObject(
            self._asap3_handle,
            self._module_handle,
            self._name.encode(RC["ENCODING"]),
            cnp_constants.TFormat.PHYSICAL_REPRESENTATION,
            ctypes.byref(cov),
        )

    @property
    def object_type(self) -> ObjectType:
        return ObjectType(self._object_info.DBObjecttype)

    @property
    def name(self) -> str:
        return self._name

    @property
    def max(self) -> float:
        return self._object_info.max

    @property
    def min(self) -> float:
        return self._object_info.min

    @property
    def max_ex(self) -> float:
        return self._object_info.maxEx

    @property
    def min_ex(self) -> float:
        return self._object_info.minEx

    @property
    def precision(self) -> int:
        return self._object_info.precision

    @property
    def value_type(self) -> ValueType:
        return ValueType(self._object_info.type)

    @property
    def unit(self) -> str:
        return self._object_info.unit.decode(RC["ENCODING"])

    @property
    def force_upload(self) -> bool:
        return self._force_upload

    @force_upload.setter
    def force_upload(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"value must be {bool}, but is {type(value)}")
        self._force_upload = value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._name})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"asap3_handle={repr(self._asap3_handle)}, "
            f"module_handle={repr(self._module_handle)}, "
            f"name={repr(self._name)}, "
            f"object_info)"
        )


class ScalarCalibrationObject(BaseCalibrationObject):
    """0D calibration object"""

    @property
    def value(self) -> float:
        cov = self._read_calibration_object_value()
        return float(cov.value.value)

    @value.setter
    def value(self, new_value: float) -> None:
        cov = self._read_calibration_object_value()
        cov.value.value = new_value
        self._write_calibration_object_value(cov)


class AxisCalibrationObject(BaseCalibrationObject):
    """1D calibration object"""

    @cached_property
    def dimension(self) -> int:
        cov = self._read_calibration_object_value()
        return cov.axis.dimension

    @property
    def axis(self) -> "npt.NDArray[np.float64]":
        cov = self._read_calibration_object_value()
        np_array = np.ctypeslib.as_array(cov.axis.axis, shape=(cov.axis.dimension,))
        return np_array.astype(dtype=float, copy=True)

    @axis.setter
    def axis(self, new_axis: typing.Sequence[float]) -> None:
        cov = self._read_calibration_object_value()
        axis = (ctypes.c_double * len(new_axis))(*new_axis)
        cov.axis.axis = axis
        self._write_calibration_object_value(cov)


class CurveCalibrationObject(BaseCalibrationObject):
    """2D Calibration Object"""

    @cached_property
    def dimension(self) -> int:
        cov = self._read_calibration_object_value()
        return cov.curve.dimension

    @property
    def axis(self) -> "npt.NDArray[np.float64]":
        cov = self._read_calibration_object_value()
        np_array = np.ctypeslib.as_array(cov.curve.axis, shape=(cov.curve.dimension,))
        return np_array.astype(dtype=float, copy=True)

    @axis.setter
    def axis(self, new_axis: typing.Sequence[float]) -> None:
        cov = self._read_calibration_object_value()
        axis = (ctypes.c_double * cov.curve.dimension)(*new_axis)
        cov.curve.axis = axis
        self._write_calibration_object_value(cov)

    @property
    def values(self) -> "npt.NDArray[np.float64]":
        cov = self._read_calibration_object_value()
        np_array = np.ctypeslib.as_array(cov.curve.values, shape=(cov.curve.dimension,))
        return np_array.astype(dtype=float, copy=True)

    @values.setter
    def values(self, values: typing.Sequence[float]) -> None:
        cov = self._read_calibration_object_value()
        c_array = (ctypes.c_double * cov.curve.dimension)(*values)
        cov.curve.values = c_array
        self._write_calibration_object_value(cov)


class MapCalibrationObject(BaseCalibrationObject):
    """3D calibration object"""

    @cached_property
    def x_dimension(self) -> int:
        cov = self._read_calibration_object_value()
        return cov.map.xDimension

    @cached_property
    def y_dimension(self) -> int:
        cov = self._read_calibration_object_value()
        return cov.map.yDimension

    @property
    def x_axis(self) -> "npt.NDArray[np.float64]":
        cov = self._read_calibration_object_value()
        np_array = np.ctypeslib.as_array(cov.map.xAxis, shape=(cov.map.xDimension,))
        return np_array.astype(dtype=float, copy=True)

    @x_axis.setter
    def x_axis(self, new_x_axis: typing.Sequence[float]) -> None:
        cov = self._read_calibration_object_value()
        c_array = (ctypes.c_double * cov.map.xDimension)(*new_x_axis)
        cov.map.xAxis = c_array
        self._write_calibration_object_value(cov)

    @property
    def y_axis(self) -> "npt.NDArray[np.float64]":
        cov = self._read_calibration_object_value()
        np_array = np.ctypeslib.as_array(cov.map.yAxis, shape=(cov.map.yDimension,))
        return np_array.astype(dtype=float, copy=True)

    @y_axis.setter
    def y_axis(self, new_y_axis: typing.Sequence[float]) -> None:
        cov = self._read_calibration_object_value()
        c_array = (ctypes.c_double * cov.map.yDimension)(*new_y_axis)
        cov.map.yAxis = c_array
        self._write_calibration_object_value(cov)

    @property
    def values(self) -> "npt.NDArray[np.float64]":
        cov = self._read_calibration_object_value()
        if cov.type == ValueType.MAP:
            np_array = np.ctypeslib.as_array(
                cov.map.values, shape=(cov.map.xDimension, cov.map.yDimension)
            )
        elif cov.type == ValueType.VAL_BLK:
            np_array = np.ctypeslib.as_array(
                cov.valblk.values, shape=(cov.valblk.xDimension, cov.valblk.yDimension)
            )
        else:
            raise ValueError
        return np_array.astype(dtype=float, copy=True)

    @values.setter
    def values(self, new_values: "npt.NDArray[np.float64]") -> None:
        cov = self._read_calibration_object_value()
        if cov.type == ValueType.MAP:
            c_array = (ctypes.c_double * (cov.map.xDimension * cov.map.yDimension))(
                *new_values.flatten()
            )
            cov.map.values = c_array
        elif cov.type == ValueType.VAL_BLK:
            c_array = (
                ctypes.c_double * (cov.valblk.xDimension * cov.valblk.yDimension)
            )(*new_values.flatten())
            cov.valblk.values = c_array
        else:
            raise ValueError
        self._write_calibration_object_value(cov)


class AsciiCalibrationObject(BaseCalibrationObject):
    @cached_property
    def len(self) -> int:
        cov = self._read_calibration_object_value()
        return cov.ascii.len

    @property
    def ascii(self) -> str:
        cov = self._read_calibration_object_value()
        return cov.ascii.ascii.decode(RC["ENCODING"])

    @ascii.setter
    def ascii(self, new_ascii: str) -> None:
        cov = self._read_calibration_object_value()
        cov.ascii.ascii = new_ascii.encode(RC["ENCODING"])
        self._write_calibration_object_value(cov)


class ValueBlockCalibrationObject(BaseCalibrationObject):
    @cached_property
    def x_dimension(self) -> int:
        cov = self._read_calibration_object_value()
        return cov.valblk.xDimension

    @cached_property
    def y_dimension(self) -> int:
        cov = self._read_calibration_object_value()
        return cov.valblk.yDimension

    @property
    def values(self) -> "npt.NDArray[np.float64]":
        cov = self._read_calibration_object_value()
        np_array = np.ctypeslib.as_array(
            cov.valblk.values, shape=(cov.valblk.xDimension, cov.valblk.yDimension)
        )
        if cov.valblk.yDimension < 2:
            np_array = np_array.flatten()
        return np_array.astype(dtype=float, copy=True)

    @values.setter
    def values(self, new_values: "npt.NDArray[np.float64]") -> None:
        cov = self._read_calibration_object_value()
        c_array = (ctypes.c_double * (cov.valblk.xDimension * cov.valblk.yDimension))(
            *new_values.flatten()
        )
        cov.valblk.values = c_array
        self._write_calibration_object_value(cov)


CalibrationObject = typing.Union[
    ScalarCalibrationObject,
    AxisCalibrationObject,
    CurveCalibrationObject,
    MapCalibrationObject,
    AsciiCalibrationObject,
    ValueBlockCalibrationObject,
]


def get_calibration_object(
    asap3_handle: cnp_class.TAsap3Hdl,  # type: ignore[valid-type]
    module_handle: typing.Union[cnp_class.TModulHdl, int],
    name: str,
) -> CalibrationObject:
    object_info = cnp_class.DBObjectInfo()
    found = cnp_prototype.Asap3GetDBObjectInfo(
        asap3_handle,
        module_handle,
        name.encode(RC["ENCODING"]),
        ctypes.byref(object_info),
    )
    if not found:
        raise KeyError(f"{name} not found.")

    cal_obj_map: typing.Dict[ValueType, typing.Type[CalibrationObject]] = {
        ValueType.VALUE: ScalarCalibrationObject,
        ValueType.CURVE: CurveCalibrationObject,
        ValueType.MAP: MapCalibrationObject,
        ValueType.AXIS: AxisCalibrationObject,
        ValueType.ASCII: AsciiCalibrationObject,
        ValueType.VAL_BLK: ValueBlockCalibrationObject,
    }
    try:
        cal_obj_type = cal_obj_map[object_info.type]
    except KeyError:
        raise TypeError(f"Calibration object {name} has unknown value type.")

    return cal_obj_type(asap3_handle, module_handle, name, object_info)
