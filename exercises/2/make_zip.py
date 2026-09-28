#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

src_dir = Path("../../src")

zip_name = datetime.now().strftime("%Y%m%d_%H%M%S_JP.zip")

with ZipFile(zip_name, "w", ZIP_DEFLATED) as zf:
    for path in src_dir.rglob("*"):
        if path.is_file():
            zf.write(path, Path("src") / path.relative_to(src_dir))

print(f"Created: {zip_name}")
