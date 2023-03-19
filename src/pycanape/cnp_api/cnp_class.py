# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

import ctypes
from ctypes import wintypes

from . import cnp_constants

enum_type = ctypes.c_uint


class tAsap3Hdl(ctypes.Structure):
    """CANaple handle"""

    _pack_ = 1


TAsap3Hdl = ctypes.POINTER(tAsap3Hdl)
TModulHdl = ctypes.c_ushort
TRecorderID = ctypes.POINTER(ctypes.c_ulong)
TTime = ctypes.c_ulong
TScriptHdl = ctypes.c_ulong

EVENT_CALLBACK = ctypes.WINFUNCTYPE(None, TAsap3Hdl, ctypes.c_ulong)


class TTaskInfo(ctypes.Structure):
    """
    :var ctypes.c_char_p description:
        description text
    :var ctypes.c_ushort taskId:
        The task id is dynamically generated by CANape
        depending on internal definitions
    :var ctypes.c_ulong taskCycle:
        Cycle rate in msec. 0 if not a cyclic task or unknown
    """

    _pack_ = 1
    _fields_ = [
        ("description", ctypes.c_char_p),
        ("taskId", ctypes.c_ushort),
        ("taskCycle", ctypes.c_ulong),
    ]


class TTaskInfo2(ctypes.Structure):
    """
    :var ctypes.c_char_p description:
        description text
    :var ctypes.c_ushort taskId:
        The task id is dynamically generated by CANape
        depending on internal definitions
    :var ctypes.c_ulong taskCycle:
        Cycle rate in msec. 0 if not a cyclic task or unknown
    :var ctypes.c_ulong eventChannel:
        event channel
    """

    _pack_ = 1
    _fields_ = [
        ("description", ctypes.c_char_p),
        ("taskId", ctypes.c_ushort),
        ("taskCycle", ctypes.c_ulong),
        ("eventChannel", ctypes.c_ulong),
    ]


class s_value(ctypes.Structure):
    """Scalar variant of :class:`TCalibrationObjectValue`.

    :var ctypes.c_uint type:
        must be :obj:`~pycanape.cnp_api.cnp_constants.ValueType.VALUE`
    :var ctypes.c_double value:
        scalar value
    """

    _pack_ = 1
    _fields_ = [
        ("type", enum_type),
        ("value", ctypes.c_double),
    ]


class s_axis(ctypes.Structure):
    """Axis variant of :class:`TCalibrationObjectValue`.

    :var ctypes.c_uint type:
        must be :obj:`~pycanape.cnp_api.cnp_constants.ValueType.AXIS`
    :var ctypes.c_short dimension:
        Number of elements
    :var ctypes.POINTER(ctypes.c_double) axis:
        array of axis values
    """

    _pack_ = 1
    _fields_ = [
        ("type", enum_type),
        ("dimension", ctypes.c_short),
        ("axis", ctypes.POINTER(ctypes.c_double)),
    ]


class s_ascii(ctypes.Structure):
    """ASCII variant of :class:`TCalibrationObjectValue`.

    :var ctypes.c_uint type:
        must be :obj:`~pycanape.cnp_api.cnp_constants.ValueType.ASCII`
    :var ctypes.c_short len:
        Number of characters
    :var ctypes.c_char_p ascii:
        array of characters
    """

    _pack_ = 1
    _fields_ = [
        ("type", enum_type),
        ("len", ctypes.c_short),
        ("ascii", ctypes.c_char_p),
    ]


class s_curve(ctypes.Structure):
    """Curve variant of :class:`TCalibrationObjectValue`.

    :var ctypes.c_uint type:
        must be :obj:`~pycanape.cnp_api.cnp_constants.ValueType.CURVE`
    :var ctypes.c_short dimension:
        Number of elements
    :var ctypes.POINTER(ctypes.c_double) axis:
        array of axis coordinates
    :var ctypes.POINTER(ctypes.c_double) values:
        array of values
    """

    _pack_ = 1
    _fields_ = [
        ("type", enum_type),
        ("dimension", ctypes.c_short),
        ("axis", ctypes.POINTER(ctypes.c_double)),
        ("values", ctypes.POINTER(ctypes.c_double)),
    ]


class s_map(ctypes.Structure):
    """Map variant of :class:`TCalibrationObjectValue`.

    :var ctypes.c_uint type:
        must be :obj:`~pycanape.cnp_api.cnp_constants.ValueType.MAP`
    :var ctypes.c_short xDimension:
        x-axis length
    :var ctypes.c_short yDimension:
        y-axis length
    :var ctypes.POINTER(ctypes.c_double) xAxis:
        array of x-axis coordinates
    :var ctypes.POINTER(ctypes.c_double) yAxis:
        array of y-axis coordinates
    :var ctypes.POINTER(ctypes.c_double) values:
        array of values
    """

    _pack_ = 1
    _fields_ = [
        ("type", enum_type),
        ("xDimension", ctypes.c_short),
        ("yDimension", ctypes.c_short),
        ("xAxis", ctypes.POINTER(ctypes.c_double)),
        ("yAxis", ctypes.POINTER(ctypes.c_double)),
        ("values", ctypes.POINTER(ctypes.c_double)),
    ]


class s_valblk(ctypes.Structure):
    """Value block variant of :class:`TCalibrationObjectValue`.

    :var ctypes.c_uint type:
        must be :obj:`~pycanape.cnp_api.cnp_constants.ValueType.VAL_BLK`
    :var ctypes.c_short xDimension:
        x-axis length
    :var ctypes.c_short yDimension:
        y-axis length
    :var ctypes.POINTER(ctypes.c_double) values:
        array of values
    """

    _pack_ = 1
    _fields_ = [
        ("type", enum_type),
        ("xDimension", ctypes.c_short),
        ("yDimension", ctypes.c_short),
        ("values", ctypes.POINTER(ctypes.c_double)),
    ]


class TCalibrationObjectValue(ctypes.Union):
    """Union of calibration object variants.

    :var ctypes.c_uint type:
        See :class:`~pycanape.cnp_api.cnp_constants.ValueType`.
        The enum value determines content of :class:`TCalibrationObjectValue`
    :var s_value value:
        contains the calibration object values if *type* is
        :obj:`~pycanape.cnp_api.cnp_constants.ValueType.VALUE`
    :var s_axis axis:
        contains the calibration object values if *type* is
        :obj:`~pycanape.cnp_api.cnp_constants.ValueType.AXIS`
    :var s_ascii ascii:
        contains the calibration object values if *type* is
        :obj:`~pycanape.cnp_api.cnp_constants.ValueType.ASCII`
    :var s_curve curve:
        contains the calibration object values if *type* is
        :obj:`~pycanape.cnp_api.cnp_constants.ValueType.CURVE`
    :var s_map map:
        contains the calibration object values if *type* is
        :obj:`~pycanape.cnp_api.cnp_constants.ValueType.MAP`
    :var s_valblk valblk:
        contains the calibration object values if *type* is
        :obj:`~pycanape.cnp_api.cnp_constants.ValueType.VAL_BLK`
    """

    _pack_ = 1
    _fields_ = [
        ("type", enum_type),
        ("value", s_value),
        ("axis", s_axis),
        ("ascii", s_ascii),
        ("curve", s_curve),
        ("map", s_map),
        ("valblk", s_valblk),
    ]


class DBObjectInfo(ctypes.Structure):
    """
    :var ~pycanape.cnp_api.cnp_constants.ObjectType DBObjecttype:
    :var ~pycanape.cnp_api.cnp_constants.ValueType type:
    :var ctypes.c_double min:
    :var ctypes.c_double max:
    :var ctypes.c_double minEx:
    :var ctypes.c_double maxEx:
    :var ctypes.c_byte precision:
    :var ctypes.c_char_p unit:
    """

    _pack_ = 1
    _fields_ = [
        ("DBObjecttype", enum_type),  # TObjectType  DBObjecttype
        ("type", enum_type),  # TValueType type
        ("min", ctypes.c_double),
        ("max", ctypes.c_double),
        ("minEx", ctypes.c_double),
        ("maxEx", ctypes.c_double),
        ("precision", wintypes.BYTE),
        ("unit", ctypes.c_char * wintypes.MAX_PATH),
    ]


class Appversion(ctypes.Structure):
    """
    :var ctypes.c_int MainVersion:
    :var ctypes.c_int SubVersion:
    :var ctypes.c_int ServicePack:
    :var ctypes.c_char_p Application:
    """

    _pack_ = 1
    _fields_ = [
        ("MainVersion", ctypes.c_int),
        ("SubVersion", ctypes.c_int),
        ("ServicePack", ctypes.c_int),
        ("Application", ctypes.c_char * 30),
    ]


class TMeasurementListEntry(ctypes.Structure):
    """
    :var ctypes.c_ushort taskId:
    :var ctypes.c_ulong rate:
    :var ctypes.c_long SaveFlag:
    :var ctypes.c_long Disabled:
    :var ctypes.c_char_p ObjectName:
    """

    _pack_ = 1
    _fields_ = [
        ("taskId", ctypes.c_ushort),
        ("rate", ctypes.c_ulong),
        ("SaveFlag", wintypes.BOOL),
        ("Disabled", wintypes.BOOL),
        ("ObjectName", ctypes.c_char_p),
    ]


class MeasurementListEntries(ctypes.Structure):
    """
    :var ctypes.c_uint ItemCount:
        number of entries
    :var ctypes.POINTER(ctypes.POINTER(TMeasurementListEntry))) Entries:
        Pointer to an array of measurement list entries
    """

    _pack_ = 1
    _fields_ = [
        ("ItemCount", ctypes.c_uint),
        ("Entries", ctypes.POINTER(ctypes.POINTER(TMeasurementListEntry))),
    ]


class version_t(ctypes.Structure):
    """
    :var ctypes.c_int dllMainVersion:
    :var ctypes.c_int dllSubVersion:
    :var ctypes.c_int dllRelease:
    :var ctypes.c_char_p osVersion:
    :var ctypes.c_int osRelease:
    """

    _pack_ = 1
    _fields_ = [
        ("dllMainVersion", ctypes.c_int),
        ("dllSubVersion", ctypes.c_int),
        ("dllRelease", ctypes.c_int),
        ("osVersion", ctypes.c_char * cnp_constants.MAX_OS_VERSION),
        ("osRelease", ctypes.c_int),
    ]


class DBFileInfo(ctypes.Structure):
    """
    :var ctypes.c_char_p asap2Fname:
    :var ctypes.c_char_p asap2Path:
    :var ~pycanape.cnp_api.cnp_constants.DBFileType type:
    """

    _pack_ = 1
    _fields_ = [
        ("asap2Fname", ctypes.c_char * wintypes.MAX_PATH),
        ("asap2Path", ctypes.c_char * wintypes.MAX_PATH),
        ("type", wintypes.BYTE),
    ]
