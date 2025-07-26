# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

import ctypes
import typing
from functools import cached_property

import numpy as np

from .cnp_api.cnp_class import (
    DBObjectInfo,
    TAsap3Hdl,
    TCalibrationObjectValue,
    TModulHdl,
    enum_type,
)
from .cnp_api.cnp_constants import ObjectType, TAsap3DataType, TFormat, ValueType
from .cnp_api.cnp_prototype import CANapeDll
from .config import RC
from .utils import CANapeError

if typing.TYPE_CHECKING:
    import numpy.typing as npt


_MULTIPLE_DIMENSION_THR: typing.Final = 2


class BaseCalibrationObject:
    def __init__(
        self,
        dll: CANapeDll,
        asap3_handle: TAsap3Hdl,  # type: ignore[valid-type]
        module_handle: typing.Union[TModulHdl, int],
        name: str,
        object_info: DBObjectInfo,
    ) -> None:
        self._dll = dll
        self._asap3_handle = asap3_handle
        self._module_handle = module_handle
        self._name = name
        self._object_info = object_info
        self._force_upload = True
        try:
            self._datatype: typing.Optional[TAsap3DataType] = self._read_datatype()
        except CANapeError:
            self._datatype = None

    def _read_datatype(self) -> TAsap3DataType:
        _dtype = enum_type(0)
        _address = ctypes.c_ulong(0)
        _min = ctypes.c_double(0)
        _max = ctypes.c_double(0)
        _increment = ctypes.c_double(0)
        self._dll.Asap3ReadObjectParameter(
            self._asap3_handle,
            self._module_handle,
            self._name.encode(RC["ENCODING"]),
            TFormat.PHYSICAL_REPRESENTATION,
            ctypes.byref(_dtype),
            ctypes.byref(_address),
            ctypes.byref(_min),
            ctypes.byref(_max),
            ctypes.byref(_increment),
        )
        return TAsap3DataType(_dtype.value)

    def _read_calibration_object_value(self) -> TCalibrationObjectValue:
        cov = TCalibrationObjectValue()
        self._dll.Asap3ReadCalibrationObject2(
            self._asap3_handle,
            self._module_handle,
            self._name.encode(RC["ENCODING"]),
            TFormat.PHYSICAL_REPRESENTATION,
            self._force_upload,
            ctypes.byref(cov),
        )
        return cov

    def _write_calibration_object_value(self, cov: TCalibrationObjectValue) -> None:
        self._dll.Asap3WriteCalibrationObject(
            self._asap3_handle,
            self._module_handle,
            self._name.encode(RC["ENCODING"]),
            TFormat.PHYSICAL_REPRESENTATION,
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
            err_msg = f"value must be {bool}, but is {type(value)}"
            raise TypeError(err_msg)
        self._force_upload = value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._name})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"asap3_handle={self._asap3_handle!r}, "
            f"module_handle={self._module_handle!r}, "
            f"name={self._name!r}, "
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
        return cov.ascii.ascii[: self.len].decode(RC["ENCODING"])

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
        if cov.valblk.yDimension < _MULTIPLE_DIMENSION_THR:
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
    dll: CANapeDll,
    asap3_handle: TAsap3Hdl,  # type: ignore[valid-type]
    module_handle: typing.Union[TModulHdl, int],
    name: str,
) -> CalibrationObject:
    object_info = DBObjectInfo()
    found = dll.Asap3GetDBObjectInfo(
        asap3_handle,
        module_handle,
        name.encode(RC["ENCODING"]),
        ctypes.byref(object_info),
    )
    if not found:
        err_msg = f"{name} not found."
        raise KeyError(err_msg)

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
        err_msg = f"Calibration object {name} has unknown value type."
        raise TypeError(err_msg) from None

    return cal_obj_type(
        dll=dll,
        asap3_handle=asap3_handle,
        module_handle=module_handle,
        name=name,
        object_info=object_info,
    )
