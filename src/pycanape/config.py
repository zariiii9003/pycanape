import sys
from typing import Any, Dict

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final


RC: Final[Dict[str, Any]] = {"ENCODING": "latin-1"}  # runtime config
