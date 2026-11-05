#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Kerem Kilic (Ellic Studio)
"""Bundle a local firmware package and browser installer for another computer.

    python3 tools/make_dev_installer.py
    python3 tools/make_dev_installer.py --package build/melodee.fwsc --output build/dev-installer.zip

This creates a development bundle, not an attested release.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
import make_site


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=ROOT / "build/melodee.fwsc")
    parser.add_argument("--output", type=Path, default=ROOT / "build/local/melodee-dev-web-installer.zip")
    args = parser.parse_args()
    package = args.package.resolve()
    output = args.output.resolve()
    if not package.is_file():
        parser.error(f"no firmware package at {package}; run ./build.sh first")
    if output.suffix != ".zip" or output == package:
        parser.error("--output must be a separate .zip file")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="melodee-dev-installer-") as temporary:
        site = Path(temporary) / "site"
        # Stable history expects a numeric version. Reserve 0.0.0 for this
        # unpublished local bundle; the firmware identity is read from the bytes.
        make_site.main(package, "0.0.0", site, installer_only=True)
        (site / "README.txt").write_text(
            "Melodee local development installer\n\n"
            "This is not a published or attested release. The installer labels it 0.0.0.\n"
            "Unzip on the computer connected to the FM-1 by USB. In the extracted folder run:\n\n"
            "  python3 -m http.server 8000 --bind 127.0.0.1\n\n"
            "Open Chrome or Edge at http://localhost:8000/webapp/installer/\n"
            "Back up your FM-1 before installing. Keep power and USB connected throughout.\n"
            "Stop the server with Ctrl+C when finished.\n\n"
            f"Input package: {package.name}\n"
            f"Firmware SHA-256: {hashlib.sha256(package.read_bytes()).hexdigest()}\n",
            encoding="utf-8")
        shutil.make_archive(str(Path(temporary) / "installer"), "zip", site)
        shutil.copyfile(Path(temporary) / "installer.zip", output)
    print(f"Development installer: {output}")


if __name__ == "__main__":
    main()
