import shutil
import subprocess
from pathlib import Path


def test_installer_passes_bash_syntax_check():
    bash = shutil.which("bash")
    assert bash is not None, "bash is required to validate the Debian-targeted installer"
    script = Path(__file__).resolve().parent.parent / "scripts" / "install-overlay.sh"
    result = subprocess.run([bash, "-n", str(script)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
