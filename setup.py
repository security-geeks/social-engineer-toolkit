#!/usr/bin/env python3
"""Packaging shim and legacy installer for SET."""

from pathlib import Path
import shutil
import subprocess
import sys


def legacy_install():
    project_root = Path(__file__).resolve().parent
    install_root = Path("/usr/local/share/setoolkit")
    config_dir = Path("/etc/setoolkit")
    launcher = Path("/usr/local/bin/setoolkit")

    print("[*] Installing requirements.txt...")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(project_root / "requirements.txt"),
    ])

    print("[*] Installing setoolkit to /usr/local/share/setoolkit")
    install_root.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    _copy_project_files(project_root, install_root)
    shutil.copy2(project_root / "src/core/config.baseline", config_dir / "set.config")

    print("[*] Creating launcher for setoolkit...")
    launcher.write_text(
        "#!/bin/sh\ncd /usr/local/share/setoolkit\n./setoolkit \"$@\"\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)

    print("[*] Finished. Run 'setoolkit' to start the Social Engineer Toolkit.")


def _copy_project_files(project_root, install_root):
    ignored = {
        ".git",
        ".github",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "venv",
    }

    for source in project_root.iterdir():
        if source.name in ignored or source.name.endswith(".egg-info"):
            continue

        destination = install_root / source.name
        if source.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(
                source,
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            shutil.copy2(source, destination)


def main():
    if len(sys.argv) == 1:
        legacy_install()
        return

    from setuptools import setup

    setup()


if __name__ == "__main__":
    main()
