import subprocess
import tempfile
from pathlib import Path


def run_python_in_docker(
    source_code: str,
    timeout: int = 10,
) -> dict:
    """Run Python source code inside an isolated Docker container."""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_file = temp_path / "main.py"

        source_file.write_text(
            source_code,
            encoding="utf-8",
        )

        command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--memory",
            "128m",
            "--cpus",
            "0.5",
            "--pids-limit",
            "64",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--user",
            "65534:65534",
            "-v",
            f"{source_file}:/app/main.py:ro",
            "python:3.12-slim",
            "python",
            "/app/main.py",
        ]

        try:
            result = subprocess.run(
                command,
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
                "stderr": (
                    f"Execution timed out after "
                    f"{timeout} seconds."
                ),
            }

        except Exception as exc:
            return {
                "success": False,
                "return_code": None,
                "stdout": "",
                "stderr": str(exc),
            }
