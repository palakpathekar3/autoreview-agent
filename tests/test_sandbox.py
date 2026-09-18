from sandbox.docker_runner import run_python_in_docker


def test_python_code_runs_successfully():
    code = """
print("sandbox success")
"""

    result = run_python_in_docker(code)

    assert result["success"] is True
    assert result["return_code"] == 0
    assert result["stdout"] == "sandbox success\n"
    assert result["stderr"] == ""


def test_python_runtime_error_is_captured():
    code = """
raise ValueError("sandbox runtime error")
"""

    result = run_python_in_docker(code)

    assert result["success"] is False
    assert result["return_code"] == 1
    assert "ValueError: sandbox runtime error" in result["stderr"]


def test_python_timeout_is_handled():
    code = """
while True:
    pass
"""

    result = run_python_in_docker(
        code,
        timeout=3,
    )

    assert result["success"] is False
    assert result["return_code"] is None
    assert result["stderr"] == (
        "Execution timed out after 3 seconds."
    )

