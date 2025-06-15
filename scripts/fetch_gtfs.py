#!/usr/bin/env python
"""
Download the latest Caltrain GTFS feed, unzip, and place it in
src/caltrain_mcp/data/caltrain-ca-us
"""

import io
import pathlib
import shutil
import tempfile
import urllib.request
import zipfile

GTFS_URL = "https://data.trilliumtransit.com/gtfs/caltrain-ca-us/caltrain-ca-us.zip"
TARGET_DIR = (
    pathlib.Path(__file__).parent.parent
    / "src"
    / "caltrain_mcp"
    / "data"
    / "caltrain-ca-us"
)


def main():
    print("Downloading GTFS…")
    with urllib.request.urlopen(GTFS_URL, timeout=60) as r:
        data = r.read()

    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            zf.extractall(td)

        # Clean and create data directory
        shutil.rmtree(TARGET_DIR, ignore_errors=True)
        shutil.copytree(td, TARGET_DIR)
        print(f"✅  GTFS refreshed in {TARGET_DIR}")


if __name__ == "__main__":
    main()
