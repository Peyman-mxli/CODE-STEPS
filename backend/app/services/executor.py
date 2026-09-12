import subprocess


def run_code(code: str):

    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--memory=100m",
                "--cpus=0.5",
                "--network=none",
                "-i",
                "codesteps-sandbox"
            ],
            input=code,
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out (5 seconds)"
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e)
        }