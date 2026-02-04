from pathlib import Path
import re

dir_path = Path("schematics")  # ← 改成你的目录

pattern = re.compile(r"^(\d+_png)\.rf\..*\.jpg$")

for p in dir_path.iterdir():
    if not p.is_file():
        continue

    m = pattern.match(p.name)
    if not m:
        continue

    new_name = f"{m.group(1)}.jpg"
    new_path = p.with_name(new_name)

    if new_path.exists():
        print(f"[SKIP] {new_name} already exists")
        continue

    p.rename(new_path)
    print(f"{p.name}  ->  {new_name}")
