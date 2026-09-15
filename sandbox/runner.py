import subprocess
import sys
from pathlib import Path


def run_python_file(
    file_path: str,
    timeout: int = 10,
) -> dict:
    """Run a Python file with a timeout and capture its result."""

    path = Path(file_path)

    if not path.exists():
        return {
            "success": False,
            "return_code": None,
            "stdout": "",
            "stderr": f"File not found: {file_path}",
        }

    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "return_code": None,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
        }

    except Exception as exc:
        return {
            "success": False,
            "return_code": None,
            "stdout": "",
            "stderr": str(exc),
        }
