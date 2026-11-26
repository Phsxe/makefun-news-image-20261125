"""news-image-20261125 entry.

The newspaper image is pre-rendered and stored beside this file as
entry.png. This program only copies it to the grader's output directory,
using the Python standard library only.
"""

import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        raise SystemExit("entry.png not found next to main.py: " + source)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = os.path.join(here, "out")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    if os.path.getsize(target) != os.path.getsize(source):
        raise SystemExit("copied entry.png has unexpected size: " + target)


if __name__ == "__main__":
    main()
