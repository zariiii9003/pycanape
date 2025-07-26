"""This is a simple script to reduce manual work when updating the symbol mapping for new CANape versions.
Call script with canapapi.h path as argument."""

import re
import sys
from pathlib import Path

PRJ_ROOT = Path(__file__).parent.parent
HEADER_PATH = Path(sys.argv[1])
PYCANAPE_PATH = PRJ_ROOT / r"C:src\pycanape\cnp_api\cnp_prototype.py"

header_text = HEADER_PATH.read_text("cp1252")
python_text = PYCANAPE_PATH.read_text("utf-8")

func_pattern = re.compile(
    r"(?:extern\s+)?(?P<restype>\w+)\s+ASAP3_EXPORT\s+CALL_CONV\s+"
    r"(?P<func_name>\w+)\s*?\((?P<func_args>.*?)\)\s*;",
    re.DOTALL,
)
arg_pattern = re.compile(
    r"^(?:const\s+)?(?P<dtype>(?:unsigned\s+)?(?:::)?\w+\s*\**)\s*(?P<name>\w+(?P<brackets>\[])?)?(?:\s*=.*?)?$"
)

FMT = """
        self.{func_name} = self._map_symbol(
            func_name="{func_name}",
            restype={restype},
            argtypes=[
{argtypes}
            ],{errcheck}
        )"""

ERRCHECK = """
            errcheck=self._get_last_error,"""

CTYPES_DICT: dict[str, str] = {
    "void*": "ctypes.c_void_p",
    "void *": "ctypes.c_void_p",
    "void**": "ctypes.POINTER(ctypes.c_void_p)",
    "char*": "ctypes.c_char_p",
    "char *": "ctypes.c_char_p",
    "char**": "ctypes.POINTER(ctypes.c_char_p)",
    "char **": "ctypes.POINTER(ctypes.c_char_p)",
    "bool": "ctypes.c_bool",
    "bool *": "ctypes.POINTER(ctypes.c_bool)",
    "int": "ctypes.c_int",
    "int*": "ctypes.POINTER(ctypes.c_int)",
    "int *": "ctypes.POINTER(ctypes.c_int)",
    "int        *": "ctypes.POINTER(ctypes.c_int)",
    "int         *": "ctypes.POINTER(ctypes.c_int)",
    "short": "ctypes.c_short",
    "short *": "ctypes.POINTER(ctypes.c_short)",
    "long": "ctypes.c_long",
    "long *": "ctypes.POINTER(ctypes.c_long)",
    "unsigned char": "ctypes.c_ubyte",
    "unsigned char *": "ctypes.POINTER(ctypes.c_ubyte)",
    "unsigned int": "ctypes.c_uint",
    "unsigned int*": "ctypes.POINTER(ctypes.c_uint)",
    "unsigned int *": "ctypes.POINTER(ctypes.c_uint)",
    "unsigned short": "ctypes.c_ushort",
    "unsigned short*": "ctypes.POINTER(ctypes.c_ushort)",
    "unsigned short *": "ctypes.POINTER(ctypes.c_ushort)",
    "unsigned long": "ctypes.c_ulong",
    "unsigned long*": "ctypes.POINTER(ctypes.c_ulong)",
    "unsigned long *": "ctypes.POINTER(ctypes.c_ulong)",
    "double *": "ctypes.POINTER(ctypes.c_double)",
    "double **": "ctypes.POINTER(ctypes.POINTER(ctypes.c_double))",
    "BYTE*": "ctypes.POINTER(wintypes.BYTE)",
    "BYTE *": "ctypes.POINTER(wintypes.BYTE)",
    "BOOL": "wintypes.BOOL",
    "BOOL *": "ctypes.POINTER(wintypes.BOOL)",
    "DWORD": "wintypes.DWORD",
    "DWORD*": "ctypes.POINTER(wintypes.DWORD)",
    "DWORD *": "ctypes.POINTER(wintypes.DWORD)",
    "UINT*": "ctypes.POINTER(wintypes.UINT)",
    "UINT *": "ctypes.POINTER(wintypes.UINT)",
    "Appversion *": "ctypes.POINTER(cnp_class.Appversion)",
    "ASAP3_EVENT_CODE": "cnp_class.enum_type",
    "DBFileInfo *": "ctypes.POINTER(cnp_class.DBFileInfo)",
    "DBObjectInfo *": "ctypes.POINTER(cnp_class.DBObjectInfo)",
    "DiagJobResponse**": "ctypes.POINTER(ctypes.POINTER(cnp_class.DiagJobResponse))",
    "DiagNumericParameter *": "ctypes.POINTER(cnp_class.DiagNumericParameter)",
    "e_RamMode": "cnp_class.enum_type",
    "e_RamMode *": "ctypes.POINTER(cnp_class.enum_type)",
    "enLabelListMode": "cnp_class.enum_type",
    "eTParameterClass": "cnp_class.enum_type",
    "eTParameterClass*": "ctypes.POINTER(cnp_class.enum_type)",
    "eTSettingsParameterType*": "ctypes.POINTER(cnp_class.enum_type)",
    "eServiceStates *": "ctypes.POINTER(cnp_class.enum_type)",
    "EnRecorderState *": "ctypes.POINTER(cnp_class.enum_type)",
    "FNCDIAGNOFIFICATION": "cnp_class.FNCDIAGNOFIFICATION",
    "MeasurementListEntries **": "ctypes.POINTER(ctypes.POINTER(cnp_class.MeasurementListEntries))",
    "SecProfileEntry*": "ctypes.POINTER(cnp_class.SecProfileEntry)",
    "TAsap3DataType *": "ctypes.POINTER(cnp_class.enum_type)",
    "TAsap3DBOType": "cnp_class.enum_type",
    "TAsap3DiagHdl": "cnp_class.TAsap3DiagHdl",
    "TAsap3DiagHdl *": "ctypes.POINTER(cnp_class.TAsap3DiagHdl)",
    "TAsap3ECUState": "cnp_class.enum_type",
    "TAsap3ECUState *": "ctypes.POINTER(cnp_class.enum_type)",
    "TAsap3FileType": "cnp_class.enum_type",
    "TAsap3Hdl": "cnp_class.TAsap3Hdl",
    "TAsap3Hdl *": "ctypes.POINTER(cnp_class.TAsap3Hdl)",
    "TApplicationID  *": "ctypes.POINTER(cnp_class.TApplicationID)",
    "TCalibrationObjectValue *": "ctypes.POINTER(cnp_class.TCalibrationObjectValue)",
    "TCalibrationObjectValueEx *": "ctypes.POINTER(cnp_class.TCalibrationObjectValueEx)",
    "TConverterInfo*": "ctypes.POINTER(cnp_class.TConverterInfo)",
    "tDriverType *": "ctypes.POINTER(cnp_class.enum_type)",
    "TeSyncOption": "cnp_class.enum_type",
    "tFifoSize": "cnp_class.TFifoSize",
    "TFormat": "cnp_class.enum_type",
    "tMeasurementState *": "ctypes.POINTER(cnp_class.enum_type)",
    "TModulHdl": "cnp_class.TModulHdl",
    "TModulHdl*": "ctypes.POINTER(cnp_class.TModulHdl)",
    "TModulHdl *": "ctypes.POINTER(cnp_class.TModulHdl)",
    "tCANapeModes*": "ctypes.POINTER(cnp_class.TCANapeModes)",
    "TLayoutCoeffs *": "ctypes.POINTER(cnp_class.TLayoutCoeffs)",
    "TLogicalChannels": "cnp_class.enum_type",
    "TObjectType": "cnp_class.enum_type",
    "TObjectType *": "ctypes.POINTER(cnp_class.enum_type)",
    "TParamTemplateHdl": "cnp_class.TParamTemplateHdl",
    "TParamTemplateHdl*": "ctypes.POINTER(cnp_class.TParamTemplateHdl)",
    "TRecorderID": "cnp_class.TRecorderID",
    "TRecorderID*": "ctypes.POINTER(cnp_class.TRecorderID)",
    "TRecorderID *": "ctypes.POINTER(cnp_class.TRecorderID)",
    "TRecorderType": "cnp_class.enum_type",
    "TRecorderType *": "ctypes.POINTER(cnp_class.enum_type)",
    "tSampleBlockObject **": "ctypes.POINTER(ctypes.POINTER(cnp_class.TSampleBlockObject))",
    "TSettingsParam*": "ctypes.POINTER(cnp_class.TSettingsParam)",
    "TScriptHdl": "cnp_class.TScriptHdl",
    "TScriptHdl *": "ctypes.POINTER(cnp_class.TScriptHdl)",
    "TScriptStatus *": "ctypes.POINTER(cnp_class.enum_type)",
    "TTaskInfo *": "ctypes.POINTER(cnp_class.TTaskInfo)",
    "TTaskInfo2 *": "ctypes.POINTER(cnp_class.TTaskInfo2)",
    "::TTime *": "ctypes.POINTER(cnp_class.TTime)",
    "TValueType *": "ctypes.POINTER(cnp_class.enum_type)",
    "version_t *": "cnp_class.version_t",
}


def remove_c_comments(c_code: str) -> str:
    # remove block comments
    _c_code = re.sub(r"/\*.*?\*/", "", c_code, flags=re.DOTALL)

    # remove line comments
    lines = [_line.split("//")[0].strip() for _line in _c_code.split("\n")]

    # remove emtpy lines
    lines = [_line for _line in lines if _line]

    # join lines
    _c_code = "\n".join(lines)
    return _c_code


header_text = remove_c_comments(header_text)

py_code_fragments: list[str] = []

for match in func_pattern.finditer(header_text):
    func_name = match["func_name"]
    func_args: list[str] = [x.strip() for x in match["func_args"].split(",")]
    ctypes_restype = CTYPES_DICT[match["restype"]]

    py_arg_lines: list[str] = []
    for func_arg in func_args:
        if match := arg_pattern.match(func_arg):
            dtype = match["dtype"].strip()
            ctypes_type = CTYPES_DICT[match["dtype"].strip()]
            if match["brackets"]:
                ctypes_type = f"ctypes.POINTER({ctypes_type})"
            direction = "<" if ctypes_type.startswith("ctypes.POINTER") else ">"
            py_arg_line = (
                16 * " "
                + f"{ctypes_type},".ljust(max(40, len(ctypes_type) + 3))
                + f"# {direction} {func_arg}"
            )
            py_arg_lines.append(py_arg_line)
        else:
            raise ValueError

    py_code_fragment = FMT.format(
        func_name=func_name,
        restype=ctypes_restype,
        argtypes="\n".join(py_arg_lines),
        errcheck=ERRCHECK if ctypes_restype == "ctypes.c_bool" else "",
    )
    py_code_fragments.append(py_code_fragment)

py_code = "\n".join(sorted(py_code_fragments))

print(py_code)
