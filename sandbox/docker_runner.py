import subprocess
import tempfile
import uuid
from pathlib import Path


DOCKER_IMAGE = "python:3.12-slim"


def run_python_in_docker(
    source_code: str,
    timeout: int = 10,
) -> dict:
    """Run Python source code inside an isolated Docker container."""

    container_name = f"autoreview-sandbox-{uuid.uuid4().hex[:12]}"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_file = temp_path / "main.py"

        source_file.write_text(
            source_code,
            encoding="utf-8",
        )

        docker_args = [
            "docker",
            "run",
            "--name",
            container_name,
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
            DOCKER_IMAGE,
            "python",
            "/app/main.py",
        ]

        process = None

        try:
            process = subprocess.Popen(
                docker_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout, stderr = process.communicate(
                timeout=timeout,
            )

            return {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
            }

        except subprocess.TimeoutExpired:
            if process is not None:
                process.kill()

                try:
                    process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    pass

            # The docker CLI may be killed while the container
            # itself is still running. Force-remove that container.
            subprocess.run(
                [
                    "docker",
                    "rm",
                    "-f",
                    container_name,
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

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
            if process is not None:
                process.kill()

                try:
                    process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    pass

            subprocess.run(
                [
                    "docker",
                    "rm",
                    "-f",
                    container_name,
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            return {
                "success": False,
                "return_code": None,
                "stdout": "",
                "stderr": str(exc),
            }
