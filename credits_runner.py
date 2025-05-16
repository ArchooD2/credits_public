import io
import sys
from credits import run_credits

def get_credits_output():
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer

    try:
        run_credits()
    finally:
        sys.stdout = sys_stdout

    return buffer.getvalue().splitlines()
