import subprocess
import tempfile
import os


def evaluate_submission(code):

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
            temp.write(code.encode("utf-8"))
            temp_path = temp.name

        result = subprocess.run(
            ["python", "-I", temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out"
        }

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)