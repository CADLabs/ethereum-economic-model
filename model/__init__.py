import sys


if sys.version_info >= (3, 8):
    from typing import TypedDict, List, Callable
else:
    from typing_extensions import TypedDict, List, Callable
