import tempfile
import time
import uuid
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound


DOCKER_IMAGE = "python:3.12-slim"


def run_python_in_docker(
    source_code: str,
    timeout: int = 10,
) -> dict:
    """Run Python source code inside an isolated Docker container."""

    container_name = (
        f"autoreview-sandbox-{uuid.uuid4().hex[:12]}"
    )

    client = None
    container = None

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_file = temp_path / "main.py"

        source_file.write_text(
            source_code,
            encoding="utf-8",
        )

        try:
            client = docker.from_env()

            try:
                client.images.get(DOCKER_IMAGE)
            except ImageNotFound:
                client.images.pull(DOCKER_IMAGE)

            container = client.containers.run(
                image=DOCKER_IMAGE,
                command=[
                    "python",
                    "/app/main.py",
                ],
                name=container_name,
                detach=True,
                network_disabled=True,
                mem_limit="128m",
                nano_cpus=500_000_000,
                pids_limit=64,
                read_only=True,
                cap_drop=["ALL"],
                security_opt=[
                    "no-new-privileges:true",
                ],
                tmpfs={
                    "/tmp": (
                        "rw,noexec,nosuid,size=64m"
                    ),
                },
                user="65534:65534",
                volumes={
                    str(source_file): {
                        "bind": "/app/main.py",
                        "mode": "ro",
                    },
                },
            )

            start_time = time.monotonic()

            while True:
                container.reload()

                if container.status in {
                    "exited",
                    "dead",
                }:
                    break

                elapsed = time.monotonic() - start_time

                if elapsed >= timeout:
                    container.kill()

                    return {
                        "success": False,
                        "return_code": None,
                        "stdout": "",
                        "stderr": (
                            f"Execution timed out after "
                            f"{timeout} seconds."
                        ),
                    }

                time.sleep(0.1)

            result = container.wait()

            return_code = result.get(
                "StatusCode",
                1,
            )

            stdout = container.logs(
                stdout=True,
                stderr=False,
            ).decode(
                "utf-8",
                errors="replace",
            )

            stderr = container.logs(
                stdout=False,
                stderr=True,
            ).decode(
                "utf-8",
                errors="replace",
            )

            return {
                "success": return_code == 0,
                "return_code": return_code,
                "stdout": stdout,
                "stderr": stderr,
            }

        except DockerException as exc:
            return {
                "success": False,
                "return_code": None,
                "stdout": "",
                "stderr": str(exc),
            }

        except Exception as exc:
            return {
                "success": False,
                "return_code": None,
                "stdout": "",
                "stderr": str(exc),
            }

        finally:
            if container is not None:
                try:
                    container.remove(
                        force=True,
                    )
                except DockerException:
                    pass

            if client is not None:
                try:
                    client.close()
                except DockerException:
                    pass
