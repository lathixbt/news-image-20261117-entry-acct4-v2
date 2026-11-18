"""Copy the pre-rendered entry.png into the output directory.

Renders nothing at run time: the image was drawn ahead of time by
draw.py and is shipped as entry.png next to this file. This
entrypoint uses only the standard library, so it runs in a bare
python:3.13 image with no imaging libraries installed.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

if not os.path.isfile(SRC):
    raise SystemExit("entry.png missing next to main.py")

os.makedirs(DST_DIR, exist_ok=True)
DST = os.path.join(DST_DIR, "entry.png")
shutil.copyfile(SRC, DST)
if os.path.getsize(DST) != os.path.getsize(SRC):
    raise SystemExit("copy incomplete: size mismatch")
print(DST, os.path.getsize(DST), "bytes")
