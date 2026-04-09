from pathlib import Path
import os
import platform
import subprocess


def ensure_output_dir(path):
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def open_file(path):
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {target}")

    if platform.system() == "Windows":
        os.startfile(str(target))
    elif platform.system() == "Darwin":
        subprocess.check_call(["open", str(target)])
    else:
        subprocess.check_call(["xdg-open", str(target)])
