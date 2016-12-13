import os
# ^ above line is needed to make sure the path is correctly set (under frozen conditions)
import sys
from contextlib import contextmanager
from contextlib import redirect_stdout

import pytest

from rrpam_wds.cli import Main

from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA
from rrpam_wds import setpath  # isort:skip # NOQA


def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd


@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
        stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    # NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied:
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout  # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            # NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied

if (len(sys.argv) > 1):  # first run tests
    output = ""
    with open('output.txt', 'w') as f, redirect_stdout(f):
        pytest.main(sys.argv[1:])
        sys.argv = [sys.argv[0]]
main = Main()
sys.exit(main.app.exec_())
