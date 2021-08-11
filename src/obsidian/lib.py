from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import Union

import rich.console

console = rich.console.Console()


#
# Copied from from boltons.fileutils
#
def mkdir_p(path: Union[str, Path]):
    """Creates a directory and any parent directories that may need to
    be created along the way, without raising errors for any existing
    directories. This function mimics the behavior of the ``mkdir -p``
    command available in Linux/BSD environments, but also works on
    Windows.
    """
    path = Path(path)
    try:
        os.makedirs(str(path))
    except OSError as exc:
        if exc.errno == errno.EEXIST and path.is_dir():
            return
        raise
