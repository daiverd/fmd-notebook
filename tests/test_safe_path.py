import pytest


def test_plain_filename_accepted(isolated):
    p = isolated.safe_file_path("hello.md")
    assert p is not None
    assert p == isolated.base_dir / "hello.md"


def test_subpath_accepted(isolated):
    p = isolated.safe_file_path("projects/foo/bar.md")
    assert p is not None
    assert p == isolated.base_dir / "projects" / "foo" / "bar.md"


@pytest.mark.parametrize("bad", [
    "../etc/passwd",
    "../../etc/passwd",
    "foo/../../etc/passwd",
    "/etc/passwd",
])
def test_traversal_rejected(isolated, bad):
    assert isolated.safe_file_path(bad) is None
