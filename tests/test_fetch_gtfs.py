import importlib.util
import io
import urllib.error
import zipfile
from pathlib import Path

import pytest

# Import fetch_gtfs module directly
_fetch_gtfs_path = Path(__file__).parent.parent / "scripts" / "fetch_gtfs.py"
_spec = importlib.util.spec_from_file_location("fetch_gtfs", _fetch_gtfs_path)
fetch_gtfs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fetch_gtfs)


def _make_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("stops.txt", "stop_id,stop_name\n1,Foo\n")
    return buf.getvalue()


def test_download_and_extract(monkeypatch, tmp_path):
    """main() should download, unzip, and move contents into TARGET_DIR."""
    fake_zip = _make_zip()

    # --- stub urllib.request.urlopen -----------------------
    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(url, timeout):
        assert url == fetch_gtfs.GTFS_URL
        assert timeout == 60
        return FakeResp(fake_zip)

    monkeypatch.setattr(fetch_gtfs.urllib.request, "urlopen", fake_urlopen)

    # --- redirect TARGET_DIR into a temp dir ---------------
    monkeypatch.setattr(fetch_gtfs, "TARGET_DIR", tmp_path / "data")

    # run it
    fetch_gtfs.main()

    target = fetch_gtfs.TARGET_DIR
    assert target.exists()
    assert (target / "stops.txt").read_text().startswith("stop_id")


def test_network_failure(monkeypatch, tmp_path):
    """main() should raise an exception when network request fails."""

    def fake_urlopen(url, timeout):
        raise urllib.error.URLError("Network error")

    monkeypatch.setattr(fetch_gtfs.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_gtfs, "TARGET_DIR", tmp_path / "data")

    with pytest.raises(urllib.error.URLError):
        fetch_gtfs.main()


def test_http_error_status(monkeypatch, tmp_path):
    """main() should raise an exception when HTTP status indicates error."""

    def fake_urlopen(url, timeout):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    monkeypatch.setattr(fetch_gtfs.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_gtfs, "TARGET_DIR", tmp_path / "data")

    with pytest.raises(urllib.error.HTTPError):
        fetch_gtfs.main()


def test_invalid_zip_file(monkeypatch, tmp_path):
    """main() should raise an exception when downloaded content is not a valid ZIP."""

    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(url, timeout):
        return FakeResp(b"invalid zip content")

    monkeypatch.setattr(fetch_gtfs.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_gtfs, "TARGET_DIR", tmp_path / "data")

    with pytest.raises(zipfile.BadZipFile):
        fetch_gtfs.main()


def test_cleanup_existing_target_dir(monkeypatch, tmp_path):
    """main() should remove existing TARGET_DIR before extracting new content."""
    fake_zip = _make_zip()

    # Create existing target directory with old content
    target_dir = tmp_path / "data"
    target_dir.mkdir(parents=True)
    old_file = target_dir / "old_file.txt"
    old_file.write_text("old content")

    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(url, timeout):
        return FakeResp(fake_zip)

    monkeypatch.setattr(fetch_gtfs.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_gtfs, "TARGET_DIR", target_dir)

    # run it
    fetch_gtfs.main()

    # Verify old content is gone and new content is present
    assert not old_file.exists()
    assert (target_dir / "stops.txt").exists()
    assert (target_dir / "stops.txt").read_text().startswith("stop_id")


def test_empty_zip_file(monkeypatch, tmp_path):
    """main() should handle empty ZIP files gracefully."""
    # Create an empty but valid ZIP file
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as _:
        pass  # Empty ZIP
    empty_zip = buf.getvalue()

    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(url, timeout):
        return FakeResp(empty_zip)

    monkeypatch.setattr(fetch_gtfs.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_gtfs, "TARGET_DIR", tmp_path / "data")

    # Should not raise an exception
    fetch_gtfs.main()

    target = fetch_gtfs.TARGET_DIR
    assert target.exists()
    # Directory should be empty (no files)
    assert list(target.iterdir()) == []


def test_zip_with_multiple_files(monkeypatch, tmp_path):
    """main() should extract all files from ZIP archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("stops.txt", "stop_id,stop_name\n1,Station A\n")
        z.writestr("routes.txt", "route_id,route_name\n1,Local\n")
        z.writestr("trips.txt", "trip_id,route_id\n1,1\n")
    multi_file_zip = buf.getvalue()

    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(url, timeout):
        return FakeResp(multi_file_zip)

    monkeypatch.setattr(fetch_gtfs.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_gtfs, "TARGET_DIR", tmp_path / "data")

    fetch_gtfs.main()

    target = fetch_gtfs.TARGET_DIR
    assert target.exists()
    assert (target / "stops.txt").exists()
    assert (target / "routes.txt").exists()
    assert (target / "trips.txt").exists()

    # Verify content
    assert (target / "stops.txt").read_text().startswith("stop_id")
    assert (target / "routes.txt").read_text().startswith("route_id")
    assert (target / "trips.txt").read_text().startswith("trip_id")
