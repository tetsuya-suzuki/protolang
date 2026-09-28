#!/usr/bin/env python3

import re
from pathlib import Path

pattern = re.compile(r"^([ \t]*)~~~", re.MULTILINE)

for path in Path(".").rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    new_text = pattern.sub(r"\1```", text)

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(path)
